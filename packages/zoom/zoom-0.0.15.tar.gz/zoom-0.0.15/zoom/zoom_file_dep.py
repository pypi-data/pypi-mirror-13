import os

from zoom_error import ZoomError
from zoom_resource import ZoomDependency
from zoom_io import download_file

class ZoomFileDep(ZoomDependency):
    def __init__(self, root, path, url,
                 filename=None):
        '''
        Initialize this file dependency.

        args:
            root: root of the ZoomProject
            path: path to this dependency
            url: url for this dependency
            filename: name to download file as
        '''
        super(ZoomFileDep, self).__init__(root, path, url)
        self.rtype = 'file'
        self.filename = filename
        if not filename:
            self.filename = self.url.split('/')[-1]
        self.identifier = os.path.join(self.path, self.filename)

    def is_synced(self):
        '''
        Check if this module is already synced

        returns:
            bool: true if synced else false
        '''
        return os.path.isfile(self.identifier)

    def status(self):
        '''
        String representation of this module's status

        returns:
            str: file downloaded or not downloaded
        '''
        if self.is_synced():
            return "file synced to: {}".format(self.identifier)
        else:
            return "file not synced"

    def sync(self):
        '''
        Sync this module to the correct state.

        raises:
            ZoomError: failed to download file
        '''
        try:
            download_file(self.url, self.abspath, self.filename)
        except IOError:
            raise ZoomError('failed to download file')

    def delete(self):
        '''
        Remove the downloaded file from the filesystem
        '''
        os.remove(self.identifier)

    def serialize(self):
        '''
        Serialize state of this dependency

        returns:
            dict: dict representation of this dependency
        '''
        return {
            'rtype': self.rtype,
            'path': self.path,
            'url': self.url,
            'filename': self.filename
        }
