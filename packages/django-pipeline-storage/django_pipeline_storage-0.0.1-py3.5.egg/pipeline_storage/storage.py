import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import filepath_to_uri
from django.utils.six.moves.urllib.parse import urljoin

from pipeline import storage

from django.contrib.staticfiles import finders

class BaseFinderStorage(object):
    finders = None

    def __init__(self, finders=None, *args, **kwargs):
        self.base_url = settings.STATIC_URL
        if finders is not None:
            self.finders = finders
        if self.finders is None:
            raise ImproperlyConfigured("The storage %r doesn't have a finders class assigned." % self.__class__)

    def exists(self, name):
        return self.finders.find(name) is not None

    def listdir(self, path):
        for finder in finders.get_finders():
            for storage in finder.storages.values():
                try:
                    return storage.listdir(path)
                except OSError:
                    pass

    def match_location(self, name, path, prefix=None):
        if prefix:
            prefix = "%s%s" % (prefix, os.sep)
            name = name[len(prefix):]
        if path == name:
            return name
        if os.path.splitext(path)[0] == os.path.splitext(name)[0]:
            return name
        return None

    def find_storage(self, name):
        for finder in finders.get_finders():
            for path, storage in finder.list([]):
                prefix = getattr(storage, 'prefix', None)
                matched_path = self.match_location(name, path, prefix)
                if matched_path:
                    return matched_path, storage
        raise ValueError("The file '%s' could not be found with %r." % (name, self))

    def open(self, name, mode="rb"):
        name, storage = self.find_storage(name)
        return storage._open(name, mode)

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urljoin(self.base_url, filepath_to_uri(name))


class PipelineFinderStorage(BaseFinderStorage):
    finders = finders


class PipelineStorage(object):

    _finders_class = PipelineFinderStorage
    _storague_class = storage.PipelineStorage

    def __init__(self, *args, **kwargs):

        self.finders = self._finders_class(*args, **kwargs)
        self.storage = self._storague_class(*args, **kwargs)
        self.is_collect = False

    def __getattr__(self, name):
        if name == "path":
            self.is_collect = True
        return getattr(self.finders if not self.is_collect else self.storage, name)
