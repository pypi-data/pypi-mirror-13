import unittest
from vcheck.versionerror import VersionError
import uuid

randmsg = uuid.uuid4().hex


# ================================
# Test VersionError
# ================================
class versionerror_test(unittest.TestCase):
    # ================================
    # Test init
    # ================================
    def init_isexception_test(self):
        self.assertTrue(issubclass(VersionError, Exception))

    # ================================
    # Test attributes
    # ================================
    def errno_test(self):
        self.assertEqual(VersionError(msg=randmsg, errno=VersionError.DIRTY).errno, VersionError.DIRTY)

    def msg_test(self):
        self.assertEqual(VersionError(msg=randmsg, errno=VersionError.DIRTY).msg, randmsg)
