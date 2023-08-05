from .checkmod import CheckMod as _CheckMod
from .versionerror import VersionError as _VersionError
import warnings as _warnings
import sys as _sys


def vcheck(mod, hexsha=None, version=None):
    """
    Checks a given module against either a git sha1 signature or a version.

    The vcheck function is designed to provide a quick
    and easy way to verify any Python module within a git
    repository.

    Parameters
    ----------
    hexsha : str
        A git sha1 signature indicating a particular commit.
    version : str
        A string indicating a particular git tag.

    Returns
    -------
    bool
        Whether the module checks out or not

    Raises
    ------
    vcheck.VersionError
        If there has been an error identifying the module version.
    """
    cm = _CheckMod(mod)
    return cm.vcheck(hexsha=hexsha, version=version)


def check_warn(mod, hexsha=None, version=None, verbose=None):
    """
    Warns if a given Python module does not match a particular git sha1
    signature or version.
    
    This function is most useful accompanying an :code:`import`.
    After importing, a version check can quickly raise a warning if the module
    code does not match or if there are difficulties checking the version.

    Parameters
    ----------
    mod : module
        An object which is a Python module.
    hexsha : str
        A git sha1 signature indicating a particular commit.
    version : str
        A string indicating a particular git tag.
    """
    try:
        check_raise(mod, hexsha=hexsha, version=version, verbose=verbose)
    except ValueError:
        raise
    except _VersionError:
        err = _sys.exc_info()
        exc = err[1]
        _warnings.warn('{}: {}'.format(err[0].__name__, exc.args[0]), stacklevel=2)


def check_raise(mod, hexsha=None, version=None, verbose=None):
    """
    Raises an error if a given Python module does not match a particular git sha1
    signature or version.
    
    This function is most useful accompanying an :code:`import`.
    After importing, a version check can quickly raise an error if the module
    code does not match or if there are difficulties checking the version.

    Parameters
    ----------
    mod : module
        An object which is a Python module.
    hexsha : str
        A git sha1 signature indicating a particular commit.
    version : str
        A string indicating a particular git tag.
    """
    cm = _CheckMod(mod)
    if not cm.vcheck(hexsha=hexsha, version=version):

        if hexsha is not None:
            raise _VersionError('Module {} with hexsha {} does not match requested: {}'.format(cm.mainmod.__name__, cm.hexsha, hexsha))
        elif version is not None:
            raise _VersionError('Module {} with version {} does not match requested: {}'.format(cm.mainmod.__name__, cm.version, version))
    else:
        if verbose is not None:
            if hexsha is not None:
                print('VCheck: Module {} matches requested hexsha {}'.format(cm.mainmod.__name__, cm.hexsha))
            elif version is not None:
                print('VCheck: Module {} matches requested version {}'.format(cm.mainmod.__name__, cm.version))
