import unittest.mock as mock
import vcheck
import git
from .base import base as _base
from .base import *


class versionmod_test(base):
    def version_noversion_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Unable to return version: not at a tag.') as cm:
            ver = vcheck.version(self.mod2check)  # noqa

        self.assertEqual(cm.exception.errno, vcheck.VersionError.NOT_AT_TAG)

    def version_valid_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        ver = vcheck.version(self.mod2check)
        self.assertEqual(ver, current_versions[on_version_ind])

    def version_dirty_test(self):
        self.mockrepo_real(is_dirty=True)
        
        with self.assertRaises(vcheck.VersionError) as cm:
            ver = vcheck.version(self.mod2check)  # noqa

        self.assertEqual(cm.exception.errno, vcheck.VersionError.DIRTY)

    def hexsha_dirty_test(self):
        self.mockrepo_real(is_dirty=True)
        
        with self.assertRaises(vcheck.VersionError) as cm:
            ver = vcheck.hexsha(self.mod2check)  # noqa

        self.assertEqual(cm.exception.errno, vcheck.VersionError.DIRTY)

    def hexsha_valid_test(self):
        hexsha = vcheck.hexsha(self.mod2check)

        self.assertEqual(hexsha, current_hexsha)
