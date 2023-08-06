#!/usr/bin/python
from __future__ import absolute_import, division, print_function

from .assemble import get_package
from pandora import Version
import click

package = get_package()


@click.group()
def main():
    """Assemble your packages!

    While developing your package, you can use the test command to run
    all the tox tests.

    \b
        assemble test
        assemble requirements-scan > requirements.txt

    When your package is ready and your repository is up-to-date, you can
    register your package, patch the version, build your distribution,
    upload it to PyPi and tag your repository.

    \b
        assemble register
        assemble version
        assemble build
        assemble upload
        assemble tag

    Or, for quick results

    \b
        assemble publish

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
@click.option('-e', '--environment', type=str, default=None)
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


@main.command('version')
@click.option('-v', '--version', type=str,
              help='new version of your package (PEP 0440)')
@click.option('-x', '--major', is_flag=True, default=False,
              help='increase the major')
@click.option('-y', '--minor', is_flag=True, default=False,
              help='increase the minor')
@click.option('-p', '--patch', is_flag=True, default=False,
              help='increase the patch')
@click.option('-d', '--dev', is_flag=True, default=False,
              help='increase the development number')
def patch_version(version, major, minor, patch, dev):
    """Patch the version of your package.

    Without providing a version, a text editor is opened with the current
    version. Save and quit to use it.

    This command checks if your repository is clean, it will fetch, diff and
    rev-list. When all is valid, it will update the content of the __init__.py
    file of the package.

    Usage examples:

    \b
        assemble version -v 1.1.5.dev4
        assemble version -p

    """
    if version is not None:
        try:
            build = Version(version)
        except ValueError:
            click.secho('Invalid version `{:s}`.'.format(version.strip()),
                        fg='red')
            raise click.Abort()
    else:
        build = Version(package.meta.version)

    if major:
        build.increase('major')
    elif minor:
        build.increase('minor')
    elif patch:
        build.increase('patch')
    elif dev:
        build.increase('dev')
    elif version is None:
        version = click.edit(str(build))
        if version is None:
            raise click.Abort()
        try:
            build = Version(version.strip())
        except ValueError:
            click.secho('Invalid version `{:s}`.'.format(version.strip()),
                        fg='red')
            raise click.Abort()

    package.patch_version(str(build))


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
@click.option('-e', '--environment', type=str, default=None)
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
@click.option('-e', '--environment', type=str, default=None)
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


@main.command('requirements-scan')
@click.option('-n', '--named', is_flag=True, default=False)
@click.option('-e', '--equal', is_flag=True, default=False)
def requirements_scan(named, equal):
    """Scan the requirements for your package.

    You can use this to create a `requirements.txt` file. It uses the AST
    of every `*.py` in the package to figure out which requirements you use.
    The current installed PIP distributions are used to determine the version.

    Usage example:

        assemble requirements-scan > requirements.txt

     """
    found, not_found = package.get_requirements(named, equal)

    for module_name in found:
        click.echo(module_name)

    if len(not_found):
        click.echo('')
        click.echo('# Could not resolve these imports')
        for module_name in not_found:
            click.echo('# ' + module_name)


@main.command('publish')
@click.option('-v', '--version', type=str,
              help='new version of your package (PEP 0440)')
@click.option('-x', '--major', is_flag=True, default=False,
              help='increase the major')
@click.option('-y', '--minor', is_flag=True, default=False,
              help='increase the minor')
@click.option('-p', '--patch', is_flag=True, default=False,
              help='increase the patch')
@click.option('-d', '--dev', is_flag=True, default=False,
              help='increase the development number')
@click.pass_context
def publish(ctx, version, major, minor, patch, dev):
    package.assert_git_is_clean()

    ctx.invoke(patch_version, version=version, major=major, minor=minor,
               patch=patch, dev=dev)
    ctx.invoke(build)
    ctx.invoke(upload)
    ctx.invoke(tag)


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
