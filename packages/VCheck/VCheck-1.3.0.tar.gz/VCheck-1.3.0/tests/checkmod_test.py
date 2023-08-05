import unittest.mock as mock
import vcheck
import git
from .base import *


class checkmod_test(base):
    # ================================
    # Test init
    # ================================
    def init_raisedirty_test(self):
        self.mockrepo_real(is_dirty=True)

        with self.assertRaises(vcheck.VersionError) as cm:
            cmod = vcheck.CheckMod(self.mod2check)  # noqa

        self.assertEqual(cm.exception.errno, vcheck.VersionError.DIRTY)

    def init_notgit_test(self):
        self.doCleanups()
        self.gitRepo_patcher = mock.patch('git.Repo', autospec=True, side_effect=git.InvalidGitRepositoryError('Mock Error'))
        self.gitRepo_patcher.start()
        self.addCleanup(self.gitRepo_patcher.stop)

        with self.assertRaises(vcheck.VersionError) as cm:
            self.cmod

        self.assertEqual(cm.exception.errno, vcheck.VersionError.NO_GIT)

    # ================================
    # Test vcheck()
    # ================================
    def vcheck_toomanyargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Only specify either hexsha (.*) or version(.*)'):
            self.cmod.vcheck(hexsha=current_hexshas[on_version_ind] , version=current_versions[on_version_ind])

    def vcheck_notenoughargs_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        with self.assertRaisesRegex(ValueError, 'Neither hexsha nor version specified'):
            self.cmod.vcheck()

    def vcheck_hexshamatches_test(self):
        self.assertTrue(self.cmod.vcheck(hexsha=current_hexsha))

    def vcheck_hexshafails_test(self):
        self.assertFalse(self.cmod.vcheck(hexsha=unpresent_hexsha))

    def vcheck_versionmatches_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        self.assertTrue(self.cmod.vcheck(version=current_versions[on_version_ind]))

    def vcheck_versionfails_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)
        
        self.assertFalse(self.cmod.vcheck(version=unpresent_version))

    def vcheck_versionerrors_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Repo for module .* does not match a released version.'):
            self.cmod.vcheck(version=unpresent_version)

    # ================================
    # Test attributes
    # ================================
    def mod_test(self):
        self.assertIs(self.cmod.mod, self.mod2check)

    def mainmod_test(self):
        self.assertIs(self.cmod.mainmod, vcheck)

    def mainmod_path_test(self):
        self.assertEqual(self.cmod.mainmod_path, vcheck.__path__[0])

    def repo_test(self):
        self.assertIs(self.cmod.repo, self.gitRepoInst)

    def hexsha_test(self):
        self.assertEqual(self.cmod.hexsha, current_hexsha)

    def version_notags_test(self):
        self.mockrepo_real(current_hexshas=[], current_versions=[])

        with self.assertRaisesRegex(vcheck.VersionError, 'The module has no version as it is not tagged.'):
            self.cmod.version

    def version_notattag_test(self):
        with self.assertRaisesRegex(vcheck.VersionError, 'Unable to return version: not at a tag.'):
            self.cmod.version

    def version_test(self):
        on_version_ind = -1
        self.mockrepo_real(on_version_ind=on_version_ind)

        self.assertEqual(self.cmod.version, current_versions[on_version_ind])
