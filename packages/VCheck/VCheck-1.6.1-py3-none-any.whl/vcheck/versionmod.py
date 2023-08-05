from .checkmod import CheckMod


def version(mod):
    """
    Returns the version information for a given module if possible.

    Parameters
    ----------
    mod : module
        An object which is a Python module.

    Returns
    -------
    version : str
        A string indicating a particular git tag.
    """
    cm = CheckMod(mod)

    return cm.version


def hexsha(mod):
    """
    Returns the hexsha information for a given module if possible.

    Parameters
    ----------
    mod : module
        An object which is a Python module.

    Returns
    -------
    hexsha : str
        A git sha1 signature indicating a particular commit.
    """
    cm = CheckMod(mod)

    return cm.hexsha
