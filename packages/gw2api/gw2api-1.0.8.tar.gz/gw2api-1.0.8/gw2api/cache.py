import os
import math
import tempfile
import time

from .util import mtime


class FileSystemCache(object):
    def __init__(self, size, root=None, lifetime=None, per_bucket=100):
        super(FileSystemCache, self).__init__()
        self.size = size
        self.root = root or tempfile.gettempdir()
        self.lifetime = lifetime
        self.per_bucket = per_bucket

        # We create a tree structure that is log(size) deep
        self.depth = int(math.ceil(math.log(self.size, self.per_bucket)) - 1)

    def get_bucket(self, key):
        parts = []
        for i in range(self.depth):
            key /= self.per_bucket
            parts.append(str(key % self.per_bucket))
        return parts[::-1]

    def get_directory(self, key):
        return os.path.join(self.root, *self.get_bucket(key))

    def get_filename(self, key, filename):
        return os.path.join(self.get_directory(key), filename)

    def has_cached(self, cache_file):
        if self.lifetime is None:
            return os.path.exists(cache_file)

        return mtime(cache_file) >= time.time() - self.lifetime

    def get(self, key, name):
        filename = self.get_filename(key, name)
        if self.has_cached(filename):
            with open(filename, "r") as fp:
                return fp.read()
        return None

    def put(self, key, name, data):
        directory = self.get_directory(key)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.get_filename(key, name), "wb") as fp:
            fp.write(data)
