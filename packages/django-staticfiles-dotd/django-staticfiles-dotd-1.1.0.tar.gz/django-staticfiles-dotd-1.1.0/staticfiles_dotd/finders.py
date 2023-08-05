import os

from django.utils._os import safe_join
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles import views
from django.contrib.staticfiles.finders import FileSystemFinder


class MyStorage(FileSystemStorage):
    def listdir(self, path):
        dirs, filenames = super(MyStorage, self).listdir(path)

        for x in dirs:
            if x.endswith('.d'):
                filenames.append(x[:-2])
                dirs.remove(x)

        return dirs, filenames

    def _open(self, path, mode):
        pathd = '%s.d' % self.path(path)

        if not os.path.isdir(pathd):
            return super(MyStorage, self)._open(path, mode)

        filenames = []
        for root, _, files in os.walk(pathd, followlinks=True):
            for filename in [os.path.join(root, x) for x in files]:
                if filename.endswith('~'):
                    continue
                filenames.append(filename)

        contents = ''
        for filename in sorted(filenames):
            with open(filename) as f:
                contents += f.read()

        return ContentFile(contents)

class DotDFinder(FileSystemFinder):
    def __init__(self, *args, **kwargs):
        super(DotDFinder, self).__init__(*args, **kwargs)

        for root, existing_storage in self.storages.items():
            filesystem_storage = MyStorage(location=root)
            filesystem_storage.prefix = existing_storage.prefix
            self.storages[root] = filesystem_storage

    def find_location(self, root, path, prefix=None):
        if prefix:
            prefix = '%s%s' % (prefix, os.sep)
            if not path.startswith(prefix):
                return None
            path = path[len(prefix):]

        path = safe_join(root, path)
        if os.path.exists(path) or os.path.isdir('%s.d' % path):
            return path
