from collections import OrderedDict as _OrderedDict, defaultdict as _defaultdict

__all__ = ['AttrMapping', 'AttrDict', 'AttrOrderedDict', 'AttrDefaultDict']


class AttrMapping(dict):
    """Provides attribute access to any mapping

    Generally, use this class only for subclassing
    """

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __dir__(self):
        return list(self.keys())


class AttrDict(AttrMapping, dict):
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 super(AttrMapping, self).__repr__())


class AttrOrderedDict(AttrMapping, _OrderedDict):
    # OrderedDict uses internal state which they don't set initially,
    # so we need to evade that
    def __getattr__(self, key):
        if key.startswith('_OrderedDict__'):
            return _OrderedDict.__getattr__(self, key)
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_OrderedDict__'):
            return _OrderedDict.__setattr__(self, key, value)
        self[key] = value

    def __delattr__(self, key):
        if key.startswith('_OrderedDict__'):
            return _OrderedDict.__delattr__(self, key)
        del self[key]

    __repr__ = _OrderedDict.__repr__


class AttrDefaultDict(AttrMapping, _defaultdict):
    def __repr__(self):
        ddrepr = _defaultdict.__repr__(self)
        return ddrepr.replace('defaultdict', self.__class__.__name__, 1)
