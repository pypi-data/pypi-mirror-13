from __future__ import absolute_import, division, print_function

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from glob import glob
from os import path
from setuptools import find_packages
from setuptools import setup
from subprocess import PIPE
from subprocess import Popen

import re
import sys

try:
    import click
except ImportError:
    click = None

_version_re = re.compile(
    '^'
    '(\d+)\.(\d+)\.(\d+)'  # minor, major, patch
    '(-[0-9A-Za-z-\.]+)?'  # pre-release
    '(\+[0-9A-Za-z-\.]+)?'  # build
    '$')


class Package(object):
    def __init__(self, package_name, setup_path, package_path):
        self.package_name = package_name
        self.setup_path = setup_path
        self.package_path = package_path
        self.meta = Meta(self.read_from_package('__init__.py'))

    def read_from_setup(self, filename):
        with open(self.get_filename_setup(filename)) as stream:
            return stream.read()

    def read_from_package(self, filename):
        with open(self.get_filename_package(filename)) as stream:
            return stream.read()

    def get_filename_setup(self, filename):
        return path.join(self.setup_path, filename)

    def get_filename_package(self, filename):
        return path.join(self.package_path, filename)

    def setup(self, keywords, classifiers, install_requires=None, **kwargs):
        return setup(name=self.meta.title,
                     description=self.meta.description,
                     license=self.meta.license,
                     url=self.meta.uri,
                     version=self.meta.version,
                     author=self.meta.author,
                     author_email=self.meta.email,
                     maintainer=self.meta.author,
                     maintainer_email=self.meta.email,
                     keywords=keywords,
                     long_description=self.read_from_setup('README.rst'),
                     packages=[self.package_name],
                     package_dir={"": "src"},
                     zip_safe=False,
                     classifiers=classifiers,
                     install_requires=install_requires,
                     **kwargs)

    def get_tox_environments(self):
        config = ConfigParser()
        config.read(self.get_filename_setup('tox.ini'))
        return filter(lambda e: not e.startswith('coverage-'),
                      config.get('tox', 'envlist').split(','))

    def recreate_tox(self, environments):
        req_txt = self.get_filename_setup('requirements.txt')
        req_dev_txt = self.get_filename_setup('requirements-dev.txt')

        req_mtimes = list()
        env_mtimes = list()

        if path.exists(req_txt):
            req_mtimes.append(path.getmtime(req_txt))
        if path.exists(req_dev_txt):
            req_mtimes.append(path.getmtime(req_dev_txt))

        for environment in environments:
            env_path = self.get_filename_setup('.tox/' + environment)
            env_mtimes.append(path.getmtime(env_path))

        if max(req_mtimes) > min(env_mtimes):
            run('tox', '--recreate', '--notest')

    def run_tests(self, environments=None, coverage=True):
        if environments is None:
            environments = self.get_tox_environments()

        self.recreate_tox(environments)

        if coverage:
            run('coverage', 'erase')

        run('detox', '-e', ','.join(environments))

        if coverage:
            print('')
            run('coverage', 'combine')
            run('coverage', 'report')
            print('')

    def patch_version(self, version):
        run('git', 'fetch', silent=True)

        if len(run('git', 'diff', '--exit-code',
                   capture=True, silent=True)):
            click.secho('There are modified files in your repository.',
                        fg='red')
            raise click.Abort()

        if len(run('git', 'diff', '--cached', '--exit-code',
                   capture=True, silent=True)):
            click.secho('There are staged files in your repository.',
                        fg='red')
            raise click.Abort()

        if int(run('git', 'rev-list', 'HEAD...origin/master', '--count',
                   capture=True, silent=True)):
            click.secho('Your repository is ahead/behind the origin.',
                        fg='red')
            raise click.Abort()

        if version is None:
            version = click.edit(self.meta.version)
            if version is None:
                raise click.Abort()
            else:
                version = version.strip()

        if _version_re.search(version) is None:
            click.secho('Invalid version value `{:s}`.'.format(version),
                        fg='red')
            click.Abort()

        assert version not in run('git', 'tag', capture=True, silent=False)

        message = 'Bumping {:s} -- {:s} to {:s}, are you sure?'.format(
            self.meta.title, self.meta.version, version)

        click.confirm(message, abort=True, default=True)

        contents = self.read_from_package('__init__.py')
        contents = re.sub(
            r'__version__ = ([\'"]){:s}\1'.format(
                re.escape(self.meta.version)),
            r'__version__ = \g<1>{:s}\g<1>'.format(version),
            contents)

        with open(self.get_filename_package('__init__.py'), 'w') as stream:
            stream.write(contents)

    def build_distribution(self, verify=True):
        # -- Build
        click.secho('Building sdist & bdist_wheel', fg='yellow')
        run('python', 'setup.py', 'sdist', 'bdist_wheel', silent=True)

        # -- Test sdist
        packages = [
            'dist/{:s}-{:s}.tar.gz'.format(self.meta.title, self.meta.version),
            'dist/{:s}-{:s}-py2.py3-none-any.whl'.format(
                self.meta.title, self.meta.version),
        ]

        for package in packages:
            package_name = package.lower().split('/')[-1].strip('-')
            name = 'venv-' + re.sub('[^a-z0-9_]+', '-', package_name)

            click.secho('Starting virtualenv {:s}'.format(name), fg='yellow')
            try:
                run('virtualenv', name, silent=True)
                run(name + '/bin/pip', 'install', '-r',
                    self.get_filename_setup('requirements-dev.txt'),
                    silent=True)
                run(name + '/bin/pip', 'install', package, silent=True)

                command = 'import {0:s}; print {0:s}.__version__'.format(
                    self.meta.package)

                outcome = run(name + '/bin/python', '-c', command,
                              capture=True)

                assert outcome.strip() == self.meta.version
                print('Version of {:s} matches, succesfully build!\n'.format(
                    self.meta.title))
            finally:
                run('rm', '-rf', name)

    def register_pypi(self, environment='test'):
        run('python', 'setup.py', 'register', '-r', environment)

    def git_tag(self):
        run('git', 'add', self.get_filename_package('__init__.py'))
        run('git', 'commit', '-m', 'Bump version to {:s}.'.format(
            self.meta.version))
        run('git', 'push')
        run('git', 'tag', 'v' + self.meta.version)
        run('git', 'push', 'origin', '--tags')

    def upload_to_pypi(self, environment='test'):
        search = 'dist/{:s}-{:s}*'.format(self.meta.title, self.meta.version)

        for filename in glob(search):
            run('twine', 'upload', '-r', environment, filename)

    def upload_documentation(self, environment='test'):
        run('python', 'setup.py', 'upload_docs', '-r', environment)


class Meta(object):
    author = None
    description = None
    email = None
    license = None
    package = None
    title = None
    uri = None
    version = None

    def __init__(self, content):
        keywords = [
            'author', 'description', 'email', 'license',
            'package', 'title', 'uri', 'version',
        ]

        def find(name):
            match = re.search(
                r'^__{:s}__ = ([\'"])(.+?)\1'.format(name),
                content, re.M)
            if not match:
                message = 'Unable to find __{:s}__ string.'.format(name)
                raise ValueError(message)
            return match.group(2)

        for keyword in keywords:
            setattr(self, keyword, find(keyword))


def get_package(origin='.', search='src'):
    origin = path.abspath(origin)
    packages = find_packages(where=path.join(origin, search))

    if len(packages) > 1:
        raise ValueError('Cannot get package, multiple found.')

    name = packages[0]
    return Package(name, origin, path.join(origin, search, name))


def run(*cmd, **kwargs):
    silent = kwargs.get('silent') is True
    capture = kwargs.get('capture') is True

    if silent or capture:
        proc = Popen(cmd, stdout=PIPE)

        lines = list()
        for line in iter(proc.stdout.readline, ''):
            if not silent:
                print(line.replace('\n', '').replace('\r', ''))
                sys.stdout.flush()
            lines.append(line)

        return ''.join(lines)
    else:
        proc = Popen(cmd)
        proc.wait()
