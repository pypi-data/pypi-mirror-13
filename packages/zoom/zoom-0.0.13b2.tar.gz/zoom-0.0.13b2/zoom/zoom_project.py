import os
import copy

import zoom_io
from zoom_error import ZoomError

from zoom_resource import ZoomDependency, ZoomModule
from zoom_git_module import ZoomGitModule
from zoom_file_dep import ZoomFileDep

resource_types = {
    'git': ZoomGitModule,
    'file': ZoomFileDep
}

class ZoomProject(object):
    '''
    Representation of an entire zoom project
    '''

    def __init__(self, create=False):
        '''
        Initialize zoom project using the cwd of the caller.

        args:
            create: will initialize a new project if true else just load
        raises:
            ZoomError: project already exists (if creating)
            ZoomError: no project exists (if loading)
            ZoomError: failed to write zoomfile
        '''
        self.name = None
        self.modules = []
        self.deps = []
        self.root = None
        self.path = os.getcwd()
        self.rel_path = None

        if create:
            self.name = os.path.basename(self.path)
            self.root = self.path
            try:
                zoom_io.create_proj_file(self.path, self.serialize())
            except IOError:
                raise ZoomError('zoom project already exists')
            self._save()
        else:
            state = None
            try:
                self.root, state = zoom_io.load_proj_file(self.path)
                self.rel_path = zoom_io.relative_path(self.root)
            except IOError:
                raise ZoomError('not inside a zoom project')
            self.deserialize(state)

    def _save(self):
        '''
        Save the state of this zoom project to the proj file

        raises:
            ZoomError: failed to save to disk
        '''
        try:
            zoom_io.save_proj_file(self.root, self.serialize())
        except IOError:
            raise ZoomError('failed to save zoom project')

    def sync(self, force=False, exact=False, limit=None,
             sync_cb=None, error_cb=None):
        '''
        Sync all resource associated with this zoom project to their
        state, as described in the zoomfile.

        args:
            force: sync resources from scratch (delete first)
            exact: sync modules to the exact commit (even if
                   they're tracking a branch)
            limit: list of relative paths to specifically sync
            sync_cb: callback on module sync (arg: ZoomModule)
            error_cb: callback on module sync error (arg: ZoomModule, error)
        '''
        # convert relative paths to abs paths
        if limit:
            limit = [os.path.abspath(l) for l in limit]

        # sync deps
        for dep in self.deps:
            if limit:
                if not in_limit(dep.abspath, limit):
                    continue
            try:
                if callable(sync_cb): sync_cb(dep)
                if force:
                    dep.delete()
                dep.sync()
            except ZoomError as e:
                if callable(error_cb): error_cb(dep, e)

        # sync scm
        for module in self.modules:
            if limit:
                if not in_limit(module.abspath, limit):
                    continue
            try:
                # pre-sync
                if callable(sync_cb): sync_cb(module)
                if force:
                    module.delete()
                module.sync(exact=exact)
            except ZoomError as e:
                if callable(error_cb): error_cb(module, e)

        # save any sync updates
        self._save()

    def get_resources(self):
        '''
        Get a list of all resources associated with this zoom project.

        returns:
            list: list of dependencies and modules
        '''
        return self.get_dependencies() + self.get_modules()

    def get_dependencies(self):
        '''
        Get a list of deps associated with this zoom project.

        returns:
            list: list of dependencies
        '''
        return copy.deepcopy(self.deps)

    def _get_module(self, path):
        '''
        Get the module that lives at path

        args:
            path: abs path to a module
        returns:
            ZoomModule: module with abspath, path. None if no match
        '''
        for m in self.modules:
            if m.abspath == path:
                return m
        return None

    def get_modules(self):
        '''
        Get a list of modules associated with this zoom project.

        returns:
            list: list of modules
        '''
        return copy.deepcopy(self.modules)

    def foreach_module(self, command, limit=None):
        '''
        Execute command in each zoom module

        args:
            command: command to execute (string)
            limit: limit command to run in modules in these paths
        returns:
            dict: dict of module to retcode, stdout, stderr
        '''
        # convert relative paths to abs paths
        if limit:
            limit = [os.path.abspath(l) for l in limit]

        outputs = {}
        for module in self.modules:
            if limit:
                if not in_limit(module.abspath, limit):
                    continue
            retcode, stdout, stderr = module.execute(command)
            results = {
                'retcode': retcode,
                'stdout': stdout,
                'stderr': stderr
            }
            outputs[str(module)] = results
        return outputs

    def add_resource(self, rtype, args):
        '''
        Add a resource to this zoom project

        args:
            rtype: type of resource being added
        returns:
            ZoomResource: copy of the new zoom resource
        raises:
            ZoomError: module name already in use
            ZoomError: failed to save zoomfile
        '''
        new_resource = load_resource(self.root, rtype, args)

        if self.root not in new_resource.abspath:
            raise ZoomError('\'{}\' is outside of zoom project'.format(new_resource.path))

        # validate no duplicate resource exists
        for resource in self.deps + self.modules:
            if new_resource.identifier.lower() == resource.identifier.lower():
                raise ZoomError('duplicate resource exists')

        # save to the correct place
        if isinstance(new_resource, ZoomDependency):
            self.deps.append(new_resource)
        else:
            self.modules.append(new_resource)

        # save the new resource
        self._save()
        return copy.copy(new_resource)

    def track_branch(self, branch, limit):
        pass

    def lock_commit(self, path, commit=None):
        '''
        Lock the specified module to the specified commit. If commit is
        None, lock to the last synced commit.

        args:
            commit: commit to lock to
            path: relative path to a module
        return:
            ZoomModule: copy of commit-locked module
        raises:
            ZoomError: if path does not point to a module
        '''
        abspath = os.path.abspath(path)
        module = self._get_module(abspath)
        if not module:
            raise ZoomError('{} is not a module'.format(path))

        module.lock_commit(commit)
        self._save()
        return copy.copy(module)

    def lock_tag(self, tag, limit=None):
        '''
        Lock modules to a specified tag.

        args:
            tag: tag to lock to
            limit: list of paths to tag lock
        return:
            list: copy of modules that got tag locked
        '''
        # convert relative paths to abs paths
        if limit:
            limit = [os.path.abspath(l) for l in limit]

        # list of modules that actually got locked
        locked = []

        # lock modules
        for module in self.modules:
            if limit:
                if not in_limit(module.abspath, limit):
                    continue
            module.lock_tag(tag)
            locked.append(copy.copy(module))

        self._save()
        return locked

    def serialize(self):
        '''
        Serialize state of this zoom project

        returns:
            dict: dict representation of this zoom project
        '''
        return {
            'name': self.name,
            'resources': {
                'dependencies': [d.serialize() for d in self.deps],
                'modules': [m.serialize() for m in self.modules]
            }
        }

    def deserialize(self, sdict):
        '''
        Load a zoom project from a serialized state

        args:
            sdict: dict representation of a zoom project
        raises:
            ZoomError: failed to deserialize
        '''
        try:
            self.name = sdict['name']
            self.deps = [load_resource(self.root,
                                       dep.pop('rtype'),
                                       dep)
                         for dep in sdict['resources']['dependencies']]
            self.modules = [load_resource(self.root,
                                          module.pop('rtype'),
                                          module)
                            for module in sdict['resources']['modules']]

        except ZoomError:
            raise ZoomError('failed to load zoomfile')


def in_limit(path, limit):
    '''
    Check if path is in limit.
    The criteria for this is a bit weird. A path is considered in limit if
    path has an _exact_ match in limit OR path's PARENT directory is a subdir
    of a path in limit.

    args:
        path: str path in question
        limit: list of paths to check against
    returns:
        bool: true if path is a subpath of any path in limit
    '''
    parent_dir = os.path.dirname(path)
    for l in limit:
        if path == l:
            return True
        if os.path.commonprefix([parent_dir, l]) == l:
            return True
    return False

def load_resource(root, rtype, rdict):
    '''
    Create the correct type of zoom resource from a serialized state

    args:
        root: path to the root of the zoom project
        rdict: type of ZoomResource to deserialize
        mdict: serialized representation of rdict ZoomResource
    returns:
        ZoomResource: rtype implementation of a ZoomResource
    raises:
        ZoomError: invalid rtype
    '''
    resource = None

    # lookup resource type
    try:
        resource = resource_types[rtype]
    except KeyError:
        raise ZoomError("invalid dependency type: {}". format(rtype))

    # get required args from rdict
    path = None
    url = None
    try:
        path = rdict.pop('path')
        url = rdict.pop('url')
    except KeyError as e:
        raise ZoomError('failed to parse resource')

    return resource(root, path, url, **rdict)
