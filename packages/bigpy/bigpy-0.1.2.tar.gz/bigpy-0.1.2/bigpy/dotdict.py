"""
A dictionary class that allows accessing keys with a "dot" syntax.
"""


class DotDict(dict):
    """
    A dictionary class that allows accessing keys as if they where attributes of the object - i.e. with
    a "dot notation"
    """
    __RESERVED_ATTRIBUTES = {'_DotDict__alt_keys', '_DotDict__alt_key_map', '_DotDict__alt_reverse_key_map'}

    def __init__(self, another_dict=None, alt_keys=False):
        """
        Initializes the dictionary instance and optionally populates it with the contents of another dictionary.

        :param another_dict: an instance of another dictionary
        :type another_dict dict
        :param alt_keys: indicates whether or not the "alternate" keys should be created
        :type alt_keys bool
        """
        super(DotDict, self).__init__()

        self.__alt_keys = alt_keys
        self.__alt_key_map = {}
        self.__alt_reverse_key_map = {}

        self.update(another_dict)

    @staticmethod
    def __process_element(v, alt_keys):
        if isinstance(v, dict):
            return DotDict(v, alt_keys)
        elif isinstance(v, list):
            return [DotDict.__process_element(x, alt_keys) for x in v]
        else:
            return v

    @staticmethod
    def __key_to_attr(key):
        key = key if isinstance(key, str) else str(key)
        # most common scenario first
        if key[0].isalpha() and key.isalnum():
            return key

        key = ''.join([c if c.isalnum() else '_' for c in key])
        if key[0].isdigit():
            key = 'a_' + key
        elif key[0] == '_':
            key = 'a' + key
        return key

    def __getattr__(self, attr):
        # check if it is an alternate key
        if self.__alt_keys:
            attr = self.__alt_reverse_key_map[attr] if attr in self.__alt_reverse_key_map else attr
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(type(self).__name__, attr))

    def __setattr__(self, key, value):
        if key in DotDict.__RESERVED_ATTRIBUTES:
            super(DotDict, self).__setattr__(key, value)
            return

        # check if it is an alternate key
        if self.__alt_keys:
            key = self.__alt_reverse_key_map[key] if key in self.__alt_reverse_key_map else key
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DotDict, self).__setitem__(key, value)
        if self.__alt_keys and key not in self.__alt_key_map:
            alt_key = DotDict.__key_to_attr(key)
            if key != alt_key:
                while alt_key in self.__alt_reverse_key_map:
                    alt_key += '_'
                self.__alt_key_map[key] = alt_key
                self.__alt_reverse_key_map[alt_key] = key

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        # check if it is an alternate key
        saved = key
        if self.__alt_keys:
            key = self.__alt_reverse_key_map[key] if key in self.__alt_reverse_key_map else key

        super(DotDict, self).__delitem__(key)

        if self.__alt_keys:
            if saved != key:
                del self.__alt_reverse_key_map[saved]
                del self.__alt_key_map[key]

    def update(self, another=None, **kwargs):
        if another:
            for key in another:
                self[key] = DotDict.__process_element(another[key], self.__alt_keys)
        for key in kwargs:
            self[key] = DotDict.__process_element(kwargs[key], self.__alt_keys)
