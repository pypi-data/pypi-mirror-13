import json
import os
import appdirs
from .utilities import Logger
from .helpers import ignored


class Cache:
    def __init__(self, appname, filename, remove_cache=False):
        self.data = {}
        self.filename = cache_filename(appname, filename)
        if remove_cache:
            with ignored(FileNotFoundError):
                os.remove(self.filename)
        else:
            self.restore()

    def get_cache_path(self):
        return self.filename

    cache_path = property(fget=get_cache_path)

    def restore(self):
        with ignored(FileNotFoundError):
            with open(self.filename, "r") as f:
                self.data = json.load(f)

    def write(self):
        base_dir = os.path.dirname(self.filename)
        os.makedirs(base_dir, exist_ok=True)
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    @Logger('key')
    def lookup_in_cache(self, key):
        try:
            if key in self.data:
                # deep check
                for each in ["poster", "link"]:
                    filename = self.data[key][each]
                    if filename is not None:
                        if not os.path.exists(filename):
                            return None

                return self.data[key]
            else:
                return None
        except KeyError:
            return None

    @Logger()
    def add(self, key, data):
        self.data[key] = data

    def __repr__(self):
        return "Cache"


class CacheEntry(dict):
    pass


def cache_filename(appname, filename):
    dirs = appdirs.AppDirs(appname, "Chris")
    return os.path.join(dirs.user_cache_dir, filename)


def cache_dir(appname):
    dirs = appdirs.AppDirs(appname, "Chris")
    return dirs.user_cache_dir
