from copy import copy
from tri.declarative import creation_ordered, declarative
from tri.struct import Struct, Frozen


__version__ = '0.8.0'


@creation_ordered
class NamedStructField(object):
    """
    Field declaration for :code:`NamedStruct` classes
    """

    def __init__(self, default=None):
        self.default = default
        super(NamedStructField, self).__init__()


def _get_declared(self):
    # Fancy getter to not stumble over our own __getitem__ implementations
    return object.__getattribute__(self, '__class__').get_declared()


def _build_kwargs(self, args, kwargs):
    members = _get_declared(self)

    if len(args) > len(members):
        raise TypeError("%s() takes at most %d arguments (%d given)" % (self.__class__.__name__, len(members), len(args)))

    values_by_name = dict(zip(members.keys(), args))
    for kwargs_name, value in kwargs.items():
        if kwargs_name in values_by_name:
            raise TypeError("%s() got multiple values for keyword argument '%s'" % (self.__class__.__name__, kwargs_name, ))
        values_by_name[kwargs_name] = value

    for kwargs_name in values_by_name:
        if kwargs_name not in members:
            raise TypeError("%s() got an unexpected keyword argument '%s'" % (self.__class__.__name__, kwargs_name))

    return {name: values_by_name.get(name, copy(field.default)) for name, field in members.items()}


@declarative(NamedStructField, add_init_kwargs=False)
class NamedStruct(Struct):
    """
    Class extending :code:`tri.struct.Struct` to only allow a defined subset of string keys.
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NamedStruct, self).__init__(**_build_kwargs(self, args, kwargs))

    def __getitem__(self, key):
        if key not in _get_declared(self):
            raise KeyError(key)
        return super(NamedStruct, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key not in _get_declared(self):
            raise KeyError(key)
        super(NamedStruct, self).__setitem__(key, value)

    def __setattr__(self, k, v):
        try:
            self[k] = v
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, k))


def named_struct(field_names, typename="NamedStruct"):
    """
    Procedural way to define a :code:`NamedStruct` subclass, similar to the :code:`named_tuple` builtin.
    """
    return _build_named_struct(NamedStruct, field_names, typename)


@declarative(NamedStructField, add_init_kwargs=False)
class NamedFrozenStruct(Frozen, NamedStruct):
    """
    Class extending :code:`tri.struct.FrozenStruct` to only allow a defined subset of string keys.
    """
    pass


def named_frozen_struct(field_names, typename='FrozenNamedStruct'):
    """
    Procedural way to define a :code:`FrozenNamedStruct` subclass, similar to the :code:`named_tuple` builtin.
    """
    return _build_named_struct(NamedFrozenStruct, field_names, typename)


def _build_named_struct(base, field_names, typename):
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = map(str, field_names)
    typename = str(typename)

    return type(typename, (base, ), {field: NamedStructField() for field in field_names})
