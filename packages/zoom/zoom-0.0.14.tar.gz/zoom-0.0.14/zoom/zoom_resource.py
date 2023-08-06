import os
import shutil

from zoom_io import run_command, posixify, relative_path

class ZoomResource(object):
    '''
    Base class for resources
    '''
    def __init__(self, root, path, url):
        '''
        Initializes zoom resource from serialized state.

        args:
            root: root of the ZoomProject
            path: path to a resource (relative path)
            url: url of resource to track
        '''
        self.rtype = None
        self.root = root
        self.path = posixify(path)
        self.url = url
        self.abspath = os.path.normpath(os.path.join(self.root, path))
        # identifier will be used to check for uniqueness amongst resources
        # up to the child class to define
        self.identifier = None

    def __str__(self):
        '''
        String representation of this object.

        returns:
            str: string representation of this object
        '''
        return "{0}::{1}".format(self.rtype, self.identifier)

    def is_synced(self):
        '''
        Check if this resource is already synced
        '''
        raise NotImplementedError()

    def sync(self):
        '''
        Sync this resource to the correct state.
        '''
        raise NotImplementedError()

    def status(self):
        '''
        String representation of this module's status
        '''
        raise NotImplementedError()

    def delete(self):
        '''
        Remove this resource from the filesystem.
        '''
        shutil.rmtree(self.abspath, ignore_errors=True)

    def serialize(self):
        '''
        Serialize state of this resource.
        '''
        raise NotImplementedError()


class ZoomDependency(ZoomResource):
    '''
    Base class for dependencies (files)
    '''
    def __init__(self, root, path, url):
        '''
        Initializes zoom dependency from serialized state.

        args:
            root: root of the ZoomProject
            path: path to the dependency (relative path)
            url: url of the dependency
        '''
        # correct path
        if not path:
            path = relative_path(root)
        super(ZoomDependency, self).__init__(root, path, url)


class ZoomModule(ZoomResource):
    '''
    Base class for modules (scm repos)
    '''
    def __init__(self, root, path, url):
        '''
        Initializes zoom module from serialized state.

        args:
            root: root of the ZoomProject
            path: path to a module (relative path)
            url: url of the module to track
        '''
        # correct path
        if not path:
            mod_name = url.split('/')[-1]
            # just in case there is an extension
            if '.' in mod_name:
                mod_name = mod_name.split('.')[0]
            path = os.path.join(relative_path(root), mod_name)
        super(ZoomModule, self).__init__(root, path, url)

    def sync(self, exact=False):
        '''
        Sync this module to the correct state

        args:
            exact: if True, ignore any tracking and sync to an exact state
        '''
        raise NotImplementedError()

    def track_branch(self, branch):
        '''
        Set this module to track the specified branch

        args:
            branch: branch to track
        '''
        raise NotImplementedError()

    def lock_commit(self, commit=None):
        '''
        Lock this module to the specified commit. If commit is None,
        lock to the last synced commit.

        args:
            commit: commit to lock to
        raises:
            ZoomError: on fail to set commit
        '''
        raise NotImplementedError()

    def lock_tag(self, tag):
        '''
        Lock this module to the specified tag

        args:
            tag: tag to lock to
        '''
        raise NotImplementedError()

    def execute(self, command):
        '''
        Execute a command inside of this module's context.

        args:
            command: command to execute (str)
        returns:
            retcode: return code of command
            stdout: stdout from command
            stderr: stderr from command
        '''
        return run_command(command, self.abspath)
