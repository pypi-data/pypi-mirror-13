from .checkmod import CheckMod


def version(mod):
    """
    Returns the version information for a given module if possible.

    Parameters
    ----------
    mod : module
        An object which is a Python module.
    """
    cm = CheckMod(mod)

    return cm.version


def hexsha(mod):
    """
    Returns the version information for a given module if possible.

    Parameters
    ----------
    mod : module
        An object which is a Python module.
    """
    cm = CheckMod(mod)

    return cm.hexsha
