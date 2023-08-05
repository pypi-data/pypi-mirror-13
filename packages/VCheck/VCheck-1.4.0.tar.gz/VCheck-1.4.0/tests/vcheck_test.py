import unittest.mock as mock
from .base import base
from .base import *  # noqa
import warnings
import vcheck
import logging


class vcheck_test(base):
    def assertNoWarnings(self, func, *args, **kwargs):
        with warnings.catch_warnings(record=True) as wrn:
            func(*args, **kwargs)

        self.assertListEqual(wrn, [])

    # ================================
    # Test vcheck function
    # ================================
    def vcheck_toomanyargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Only specify either hexsha (.*) or version(.*)'):
            vcheck.vcheck(self.mod2check, hexsha=current_hexshas[on_version_ind] , version=current_versions[on_version_ind])

    def vcheck_notenoughargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Neither hexsha nor version specified'):
            vcheck.vcheck(self.mod2check)

    def vcheck_hexshamatches_test(self):
        self.assertTrue(vcheck.vcheck(self.mod2check, hexsha=current_hexsha))

    def vcheck_hexshafails_test(self):
        self.assertFalse(vcheck.vcheck(self.mod2check, hexsha=unpresent_hexsha))

    def vcheck_versionmatches_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        self.assertTrue(vcheck.vcheck(self.mod2check, version=current_versions[on_version_ind]))

    def vcheck_versionfails_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        self.assertFalse(vcheck.vcheck(self.mod2check, version=unpresent_version))

    def vcheck_versionerrors_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Repo for module .* does not match a released version.'):
            vcheck.vcheck(self.mod2check, version=unpresent_version)

    # ================================
    # Test check_warn function
    # ================================
    def check_warn_toomanyargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Only specify either hexsha (.*) or version(.*)'):
            vcheck.check_warn(self.mod2check, hexsha=current_hexshas[on_version_ind] , version=current_versions[on_version_ind])

    def check_warn_notenoughargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Neither hexsha nor version specified'):
            vcheck.check_warn(self.mod2check)

    def check_warn_hexshamatches_test(self):
        self.assertNoWarnings(vcheck.check_warn, self.mod2check, hexsha=current_hexsha)

    def check_warn_hexshafails_test(self):
        with self.assertWarnsRegex(UserWarning, 'Module .* with hexsha .* does not match requested: .*'):
            vcheck.check_warn(self.mod2check, hexsha=unpresent_hexsha)

    def check_warn_versionmatches_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        self.assertNoWarnings(vcheck.check_warn, self.mod2check, version=current_versions[on_version_ind])

    def check_warn_versionfails_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        with self.assertWarnsRegex(UserWarning, 'Module .* with version .* does not match requested: .*'):
            vcheck.check_warn(self.mod2check, version=unpresent_version)

    def check_warn_versionerrors_test(self):
        with self.assertWarnsRegex(UserWarning, 'Repo for module .* does not match a released version.'):
            vcheck.check_warn(self.mod2check, version=unpresent_version)

    def check_warn_verbosehexsha_test(self):
        with mock.patch('builtins.print', autospec=True) as m:
            vcheck.check_warn(self.mod2check, hexsha=current_hexsha, verbose=True)

            self.assertEqual(m.call_count, 1)
            self.assertRegex(m.call_args[0][0], 'VCheck: Module vcheck matches requested hexsha .*')

    def check_warn_verboseversion_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with mock.patch('builtins.print', autospec=True) as m:
            vcheck.check_warn(self.mod2check, version=current_versions[on_version_ind], verbose=True)

            self.assertEqual(m.call_count, 1)
            self.assertRegex(m.call_args[0][0], 'VCheck: Module vcheck matches requested version .*')

    # ================================
    # Test check_raise function
    # ================================
    def check_raise_toomanyargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Only specify either hexsha (.*) or version(.*)'):
            vcheck.check_raise(self.mod2check, hexsha=current_hexshas[on_version_ind] , version=current_versions[on_version_ind])

    def check_raise_notenoughargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Neither hexsha nor version specified'):
            vcheck.check_raise(self.mod2check)

    def check_raise_hexshamatches_test(self):
        vcheck.check_raise(self.mod2check, hexsha=current_hexsha)

    def check_raise_hexshafails_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Module .* with hexsha .* does not match requested: .*'):
            vcheck.check_raise(self.mod2check, hexsha=unpresent_hexsha)

    def check_raise_versionmatches_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        vcheck.check_raise(self.mod2check, version=current_versions[on_version_ind])

    def check_raise_versionfails_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        with self.assertRaisesRegex(vcheck.VersionError, 'Module .* with version .* does not match requested: .*'):
            vcheck.check_raise(self.mod2check, version=unpresent_version)

    def check_raise_versionerrors_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Repo for module .* does not match a released version.'):
            vcheck.check_raise(self.mod2check, version=unpresent_version)

    def check_raise_verbosehexsha_test(self):
        with mock.patch('builtins.print', autospec=True) as m:
            vcheck.check_raise(self.mod2check, hexsha=current_hexsha, verbose=True)

            self.assertEqual(m.call_count, 1)
            self.assertRegex(m.call_args[0][0], 'VCheck: Module vcheck matches requested hexsha .*')

    def check_raise_verboseversion_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with mock.patch('builtins.print', autospec=True) as m:
            vcheck.check_raise(self.mod2check, version=current_versions[on_version_ind], verbose=True)

            self.assertEqual(m.call_count, 1)
            self.assertRegex(m.call_args[0][0], 'VCheck: Module vcheck matches requested version .*')
