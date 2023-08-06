#!/usr/bin/python
from __future__ import absolute_import, division, print_function

import click
from .assemble import get_package

package = get_package()


@click.group()
def main():
    """Assemble your packages!

    While developing your package, you can use the test command to run
    all the tox tests.

    \b
        assemble test

    When your package is ready and your repository is up-to-date, you can
    register your package, patch the version, build your distribution,
    upload it to PyPi and tag your repository.

    \b
        assemble register
        assemble patch-version
        assemble build
        assemble upload
        assemble tag

    Assemble uploads to the PyPi test-environment, is your package ready
    for the world, simply supply the pypi environment

    \b
        assemble upload -e pypi

    """
    pass


@main.command('test')
@click.option('-e', '--environments', type=str,
              help='the tox environment(s) to run, separate by ","')
@click.option('--coverage/--no-coverage', default=True,
              help='capture the code-coverage of your package')
def test(environments, coverage):
    """Run the tox-tests for your package.

    You can use the -e/--environments option to specify which environments
    to run, handy if you are tinkering with your flake8 checks (for example).

    Usage examples:

    \b
        assemble test -e flake8
        assemble test --no-coverage

    """
    if environments is not None:
        environments = environments.split(',')
    package.run_tests(environments, coverage)


@main.command('register')
@click.option('-e', '--environment', type=str, default='test')
def register(environment):
    """Register your package on PyPi.

    Make sure you have tested your package first. The environment matches the
    environments you specify in your ~/.pypirc file. You should only have
    to do this once per environment.

    Usage examples:

    \b
        assemble register -e pypi

    """
    package.register_pypi(environment)


@main.command('patch-version')
@click.option('-v', '--version', type=str,
              help='new version of your package (PEP 0440)')
def patch_version(version):
    """Patch the version of your package.

    Without providing a version, a text editor is opened with the current
    version. Save and quit to use it.

    This command checks if your repository is clean, it will fetch, diff and
    rev-list. When all is valid, it will update the content of the __init__.py
    file of the package.

    Usage examples:

    \b
        assemble patch-version -v 1.1.5.dev4

    """
    package.patch_version(version)


@main.command('build')
@click.option('--verify/--skip-verify', default=True,
              help='run virtualenvs to test the distributions')
def build(verify):
    """Build sdist and wheel distributions.

    When the distributions are build, you can use --verify (default)
    to verify the builds. These will simply import the package and
    check if the version matches the required version.

    Usage examples:

    \b
        assemble build

    """
    package.build_distribution(verify)


@main.command('upload')
@click.option('-e', '--environment', type=str, default='test')
@click.option('-d', '--documentation', is_flag=True, default=False)
def upload(environment, documentation):
    """Upload your distributions to PyPi.

    Make sure you have tested, patched and build your package first (in that
    order). The environment matches the environments you specify in your
    ~/.pypirc file.

    Usage examples:

    \b
        assemble upload -e pypi
        assemble upload -d

    """
    package.upload_to_pypi(environment)
    if documentation:
        package.upload_documentation(environment)


@main.command('upload-documentation')
@click.option('-e', '--environment', type=str, default='test')
def upload_documentation(environment):
    """Upload your documenation to PyPi.

    Make sure you have tested package first (that will build your
    documentation). The environment matches the environments you specify in
    your ~/.pypirc file.

    Usage examples:

    \b
        assemble upload-documentation -e pypi

    """
    package.upload_documentation(environment)


@main.command('tag')
def tag():
    """Tag your repository with the current version.

    Make sure you have tested, patched and build your package first (in that
    order). You can do this before or after the upload.

    Usage examples:

    \b
        assemble tag

    """
    package.git_tag()
