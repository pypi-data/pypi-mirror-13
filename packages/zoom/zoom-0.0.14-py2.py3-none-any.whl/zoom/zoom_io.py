import os
import yaml
import urllib
import contextlib
import subprocess

from subprocess import PIPE

from zoom_error import ZoomError

ZOOM_FILE = "zoom.yml"

# os-independent root directory
root_dir = os.path.abspath(os.sep)

def relative_path(base):
    '''
    Get path of cwd relative to base path.

    args:
        base: path to get path relative to
    '''
    return os.getcwd().replace(base, '').strip(os.sep)

def find_proj_file(path):
    '''
    Search path and parents directories for a project file
    until one is found. Or not.

    args:
        path: path to start looking for a project file in
    returns:
        string: full path of proj file
    raises:
        IOError: file could not be found in path or parent dirs
    '''
    projfile = None
    search_path = path
    while True:
        projfile = os.path.join(search_path, ZOOM_FILE)

        if os.path.exists(projfile):
            return projfile

        search_path = os.path.dirname(search_path)
        if search_path == root_dir:
            raise IOError()

def in_zoom_project(path):
    '''
    Checks if path is within a zoom project.

    args:
        path: path in question
    returns:
        bool: true if in zoom project else false
    '''
    try:
        find_proj_file(path)
    except IOError:
        return False
    return True

def in_zoom_project_root(path):
    '''
    Checks if path is the root of a zoom project

    args:
        path: path in question
    returns:
        bool: true if in root of zoom project else false
    '''
    try:
        projfile = find_proj_file(path)
        return os.path.dirname(projfile) == path
    except IOError:
        return False

def create_proj_file(root, content):
    '''
    Create new project file, if it does not already exist.

    args:
        root: path to create project file in
        content: dictionary representing the contents of the file
    raises:
        IOError: project file already exists
    '''
    if in_zoom_project_root(root):
        raise IOError()
    else:
        save_proj_file(root, content)

def save_proj_file(root, content):
    '''
    Write content to a zoom project file.

    args:
        root: root of a zoom project
        content: dictionary representing the contents of the file
    raises:
        IOError: failed to write to file
    '''
    projfile = os.path.join(root, ZOOM_FILE)
    with open(projfile, 'w+') as f:
        f.write(yaml.dump(content, default_flow_style=False))

def load_proj_file(path):
    '''
    Loads contents of a zoom project file.

    args:
        path: path within a zoom project
    returns:
        string: dir where project file was found
        dict: contents of project file
    raises:
        IOError: file could not be found
    '''
    projfile = None
    try:
        projfile = find_proj_file(path)
    except IOError:
        raise IOError()
    with open(projfile, 'r') as f:
        return (os.path.dirname(projfile), yaml.load(f.read()))

@contextlib.contextmanager
def path_context(path):
    '''
    Context manager for a given path. cd in and cd out.
    Creates directory if it does not exist.

    args:
        path: path to cd into
    '''
    prev_cwd = os.getcwd()
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

def download_file(url, path, filename):
    '''
    Download file to path with name filename if it DNE.
    Will create directories.

    args:
        url: url to download
        path: dir to place file
        filename: name of file
    raises:
        IOError: failed to download file
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, filename)
    if not os.path.exists(filepath):
        # raises IOError on fail
        urllib.urlretrieve(url, filepath)

def run_command(command, path):
    '''
    Run command in path.

    args:
        command: command to run in list form
        path: dir to run in
    returns:
        int: return code of command
        str: stdout from command
        str: stderr from command
    raises:
        None
    '''
    # this could use Popen's cwd arg, but path_context will
    # handle the case the directory doesn't already exist
    with path_context(path):
        process = subprocess.Popen(command,
                                   shell=True,
                                   stdout=PIPE,
                                   stderr=PIPE)
        out, err = process.communicate()
        retcode = process.returncode
        return (retcode, out.strip(), err.strip())

def is_windows():
    '''
    Check if running on Windows.

    returns:
        bool: true if executed on windows, else false
    '''
    return os.name == 'nt'

def posixify(string):
    '''
    Converts Windows-badness to posixy-goodness.
    Basically just swaps '\' for '/'

    args:
        string: str to convert
    returns:
        str: converted string
    '''
    if is_windows():
        return string.replace('\\', '/')
    else:
        return string
