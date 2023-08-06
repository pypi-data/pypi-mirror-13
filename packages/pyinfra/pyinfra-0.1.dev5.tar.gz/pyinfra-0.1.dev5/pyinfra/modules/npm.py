# pyinfra
# File: pyinfra/modules/npm.py
# Desc: manage NPM packages

from pyinfra.api import operation

from .util.packaging import ensure_packages


@operation
def packages(state, host, packages=None, present=True, directory=None):
    '''
    Manage npm packages.

    + packages: list of packages to ensure
    + present: whether the packages should be present
    + directory: directory to manage packages for, defaults to global
    '''

    current_packages = (
        host.npm_packages
        if directory is None
        else host.npm_local_packages(directory)
    )

    install_command = (
        'npm install -g'
        if directory is None
        else 'cd {0} && npm install'.format(directory)
    )

    uninstall_command = (
        'npm uninstall -g'
        if directory is None
        else 'cd {0} && npm uninstall'.format(directory)
    )

    return ensure_packages(
        packages, current_packages, present,
        install_command=install_command,
        uninstall_command=uninstall_command
    )
