import unittest as _unittest
import unittest.mock as _mock
import git
import vcheck
import vcheck.versionerror as _mod2check
# ================================
# Hexsha for repo head
# ================================
current_hexsha   = 'b39035318052f36e8347c54b2dba4195a03c7847'

# ================================
# Hexsha for repo tags
# ================================
current_hexshas  = [ 'b56a895c7a5996f13341023033ab324ada6ee2bc',
                     '093f93188ce93e2ab5e2453c1423bcf87542c08b',
                     '1109ccbc8ffa750db7f0a71523d18833d54904a5'
                     ]
# ================================
# Hexsha guaranteed not present
# ================================
unpresent_hexsha = '0ff92d0c2b192ffcc136108d6c339d742da3d5f0'

# ================================
# Versions for repo tags
# ================================
current_versions  = [ 'v0.0.0', 'v0.0.1', 'v1.0.0' ]

# ================================
# Version guaranteed not present
# ================================
unpresent_version = 'v2.0.0'

# ================================
# Module to check
# ================================


class base(_unittest.TestCase):
    def setUp(self):
        # ================================
        # Create patchers
        # ================================
        self.gitRepo_patcher   = _mock.patch('git.Repo', autospec=True)
        self.gitTagRef_patcher = _mock.patch('git.TagReference', autospec=True)

        # ================================
        # Start patchers
        # ================================
        self.gitRepo_patcher.start()
        self.gitTagRef_patcher.start()

        # ================================
        # Add cleanup
        # ================================
        self.addCleanup(self.gitRepo_patcher.stop)
        self.addCleanup(self.gitTagRef_patcher.stop)
        self.addCleanup(self._clearcmod)

        self.gitRepoInst = git.Repo()

        self.mockrepo_real()

    def tearDown(self):
        pass

    def mockrepo_real(self, is_dirty=False, on_version_ind=None, current_hexshas=current_hexshas, current_versions=current_versions):
        inst = self.gitRepoInst
        # ================================
        # Set whether dirty or real
        # ================================
        inst.is_dirty.return_value = is_dirty

        # ================================
        # Mock repo has versions/tags
        # ================================
        if on_version_ind is not None:
            inst.head.object.hexsha = current_hexshas[on_version_ind]
        else:
            inst.head.object.hexsha = current_hexsha

        inst.tags = []
        for i in current_versions:
            inst.tags.append(git.TagReference('a', 'b'))

        for i, tag in enumerate(inst.tags):
            tag.object.hexsha = current_hexshas[i]
            tag.name = current_versions[i]

        # ================================
        # Reset self.cmod instance
        # ================================
        self._cmod = None

    @property
    def cmod(self):
        if self._cmod is None:
            self._cmod = vcheck.CheckMod(self.mod2check)

        return self._cmod

    def _clearcmod(self):
        self._cmod = None

    @property
    def mod2check(self):
        return _mod2check
