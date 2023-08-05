class VersionError(Exception):
    """
    Custom exceptions specific to different errors while version-checking.

    While version-checking, there are quite a few errors that can arise.
    Most are related to the state of the git repository not reliably
    reproducing a specific version. Different exceptions with varying
    `errno` codes can be raised. Codes are used to programmatically
    identify different types of failures.

    Parameters
    ----------
    msg : str
        A short error message explaining the nature of the error.
    errno : int
        A preset number taken from the :class:`vcheck.VersionError` class.

    Attributes
    ----------
    VERSION_UNMATCHED : code
        Failure because the git repository's version was not found.
    DIRTY : code
        Failure because the git repository was dirty.
    NO_GIT : code
        Failure because the module is not contained in a git repository.
    NO_TAGS : code
        Failure because the git repository has no tags.
    NOT_AT_TAG : code
        Failure because the git repository is not at any tag.
    """
    VERSION_UNMATCHED = 1
    DIRTY             = 2
    NO_GIT            = 3
    NO_TAGS           = 4
    NOT_AT_TAG        = 5

    def __init__(self, msg, errno=None):
        redmsg = '\033[31m{}\033[0m'.format(msg)
        super().__init__(redmsg)
        self._msg   = redmsg
        self._errno = errno

    @property
    def msg(self):
        """
        A short error message explaining the nature of the error.
        """
        return self._msg

    @property
    def errno(self):
        """
        A preset number taken from the :class:`vcheck.VersionError` class.
        """
        return self._errno
