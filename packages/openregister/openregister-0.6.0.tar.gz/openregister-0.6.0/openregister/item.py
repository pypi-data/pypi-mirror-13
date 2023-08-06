from .datatypes.digest import git_hash, base32_encode


class Item(object):
    """An Item, a content addressable set of attributes."""
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __getitem__(self, key, default=None):
        try:
            return self.__dict__[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return value

    def get(self, key, default=None):
        return self.__getitem__(key, default)

    def set(self, key, value):
        return self.__setitem__(key, value)

    @property
    def hash(self):
        """The git hash-object value of for the Item."""
        return git_hash(self.json.encode("utf-8"))

    @property
    def hashkey(self):
        """The hash value as a RFC 3548 Base 32 encoded string."""
        return base32_encode(self.hash)

    @property
    def keys(self):
        return sorted(list(self.primitive.keys()))

    @property
    def values(self):
        return (self.__dict__[key] for key in self.keys)
