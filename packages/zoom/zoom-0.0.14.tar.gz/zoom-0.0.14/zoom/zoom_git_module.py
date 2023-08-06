import os

from zoom_error import ZoomError
from zoom_resource import ZoomModule

GIT_DIR = '.git'

GIT_INIT = 'git init'
GIT_STATUS = 'git status'
GIT_ADD_REMOTE = 'git remote add origin {}'
GIT_FETCH = 'git fetch origin'
GIT_CHECKOUT = 'git checkout {}'
GIT_PULL = 'git pull origin {}'
GIT_REV_PARSE = 'git rev-parse HEAD'

class ZoomGitModule(ZoomModule):
    def __init__(self, root, path, url,
                 branch=None, tag=None, commit=None):
        '''
        Initialize zoom git module.

        args:
            root: root of the ZoomProject
            path: path to this module
            url: url for this dependency
            branch: branch to track
            tag: tag to lock to
            commit: commit to lock to
        '''
        super(ZoomGitModule, self).__init__(root, path, url)
        self.identifier = self.path
        self.rtype = 'git'
        self._set_revision(branch=branch, tag=tag, commit=commit)

    def _set_revision(self, branch=None, tag=None, commit=None):
        '''
        Single function to manage the logic of what pieces of information
        can be stored simultaneously.

        valid combos:
            1. branch
            2. tag
            3. commit
            4. branch + commit
            5. tag + commit
        the only invalid combos involve branch + tag, meaning simply that case
        must be disallowed. if that case is encountered, track branch.

        args:
            branch: branch to track
            tag: tag to lock to
            commit: commit to lock to
        '''
        # disallowed case, favor branch
        if branch and tag:
            tag = None
        self.branch = branch
        self.tag = tag
        self.commit = commit
        if not (self.branch or self.tag or self.commit):
            self.branch = 'master'

    def _is_git_repo(self):
        '''
        Check if this is a git repo

        returns:
            bool: true if git repo else false
        '''
        git_dir = os.path.join(self.abspath, GIT_DIR)
        return os.path.exists(git_dir)

    def _get_sha(self):
        '''
        Return the sha of the current git repo.

        returns:
            str: sha (git hash)
        raises:
            ZoomError: if this is not a git repo
        '''
        if not self._is_git_repo():
            raise ZoomError("not a git repo")
        _, stdout, _ = self.execute(GIT_REV_PARSE)
        return stdout.strip()

    def is_synced(self):
        '''
        Check if this module is already synced

        returns:
            bool: true if synced else false
        '''
        # Checking if this is a git repo is good enough
        return self._is_git_repo()

    def status(self):
        '''
        String representation of this module's status

        returns:
            str: status (stdout of git status)
        '''
        if self.is_synced():
            _, stdout, _ = self.execute(GIT_STATUS)
            return stdout
        else:
            return "repo not synced"

    def sync(self, exact=False):
        '''
        Sync this module to the correct state and store any updated info.

        args:
            exact: sync to the exact commit, even if tracking a branch
        raises:
            ZoomError: passes git stderr up if git commands fail
            ZoomError: if exact sync is called but there is no commit
        '''
        if exact and not self.commit:
            raise ZoomError('no exact commit for exact sync')

        # init repo if not already there
        if not self._is_git_repo():
            self.execute(GIT_INIT)
            self.execute(GIT_ADD_REMOTE.format(self.url))

        # fetch changes
        retcode, _, stderr = self.execute(GIT_FETCH)
        if retcode != 0:
            raise ZoomError(stderr)

        # detemine whether this is tracking a branch or locking to a commit
        track = self.branch and not exact

        if track:
            # check out this branch and pull in changes
            retcode, _, stderr = self.execute(GIT_CHECKOUT.format(self.branch))
            if retcode != 0:
                raise ZoomError(stderr)
            retcode, _, stderr = self.execute(GIT_PULL.format(self.branch))
            if retcode != 0:
                raise ZoomError(stderr)
        else:
            # check out the target commit or tag
            target_commit = self.commit or self.tag
            if exact:
                target_commit = self.commit
            retcode, _, stderr = self.execute(GIT_CHECKOUT.format(target_commit))
            if retcode != 0:
                raise ZoomError(stderr)

        # update the commit in case it changed
        self.commit = self._get_sha()

    def track_branch(self, branch):
        '''
        Set this module to track the specified branch

        args:
            branch: branch to track
        '''
        self._set_revision(branch=branch)

    def lock_commit(self, commit=None):
        '''
        Lock this module to the specified commit. If commit is None,
        lock to the last synced commit.

        args:
            commit: commit to lock to
        raise:
            ZoomError: if no commit is available to lock to
        '''
        if not commit:
            commit = self.commit
        if not commit:
            raise ZoomError('no commit specified')
        self._set_revision(commit=commit)

    def lock_tag(self, tag):
        '''
        Lock this module to the specified tag

        args:
            tag: tag to lock to
        '''
        self._set_revision(tag=tag)

    def serialize(self):
        '''
        Serialize state of this module.

        returns:
            dict: dict representation of this module
        '''
        mdict = {
            'rtype': self.rtype,
            'path': self.path,
            'url': self.url
        }
        if self.branch:
            mdict['branch'] = self.branch
        if self.tag:
            mdict['tag'] = self.tag
        if self.commit:
            mdict['commit'] = self.commit

        return mdict
