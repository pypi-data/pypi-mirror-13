import six
import os
import shutil
import warnings
import tempfile
import importlib
import pkgutil
import inspect
import string
import random

from decimal import Decimal
from collections import OrderedDict

###########################################################
# Mixins
###########################################################

class ClassDictMixin():
    """
    Dict which can be accessed via class attributes
    Thanks http://www.goodcode.io/blog/python-dict-object/
    """
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class HashableDictMixin(object):
    def __hash__(self):
        """
        This /should/ allow object to be hashable, for use in a set
        XXX: Needs UT

        Thanks Raymond @ http://stackoverflow.com/a/16162138/1267398
        """
        return hash((frozenset(self), frozenset(self.values())))


###########################################################
# Hashable dict
###########################################################


class ClassDict(ClassDictMixin, dict):
    """
    >>> d = ClassDict(hello="world")
    >>> d.hello
    'world'
    >>> d.get('hello')
    'world'
    >>> d.hello = 'wtf'
    >>> d.hello
    'wtf'
    >>> d['hello']
    'wtf'
    >>> d.world
    Traceback (most recent call last):
    AttributeError:
    >>> del d.hello
    >>> del d.world
    Traceback (most recent call last):
    AttributeError:
    """

class HashableDict(HashableDictMixin, dict):
    """
    >>> hash(HashableDict(a=1, b=2)) is not None
    True
    """


class HashableOrderedDict(HashableDictMixin, OrderedDict):
    """
    >>> hash(HashableOrderedDict(a=1, b=2)) is not None
    True
    """


def ensure_type(value, types):
    """
    Ensure value is an instance of a certain type

    >>> ensure_type(1, [str])
    Traceback (most recent call last):
    TypeError:

    >>> ensure_type(1, str)
    Traceback (most recent call last):
    TypeError:

    >>> ensure_type(1, int)
    >>> ensure_type(1, (int, str))

    :attr types: Type of list of types
    """
    if not isinstance(value, types):
        raise TypeError(
            "expected instance of {}, not {}".format(
                types, type(value)))


def touch(path, times=None):
    """
    Implements unix utility `touch`
    XXX: Needs UT

    :attr fname: File path
    :attr times: See `os.utime()` for args
                 https://docs.python.org/3.4/library/os.html#os.utime
    """
    with open(path, 'a'):
        os.utime(path, times)


def import_recursive(path):
    """
    Recursively import all modules and packages
    Thanks http://stackoverflow.com/a/25562415/1267398
    XXX: Needs UT

    :attr path: Path to package/module
    """
    results = {}
    obj = importlib.import_module(path)
    results[path] = obj
    path = getattr(obj, '__path__', os.path.dirname(obj.__file__))
    for loader, name, is_pkg in pkgutil.walk_packages(path):
        full_name = obj.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if is_pkg:
            results.update(import_recursive(full_name))
    return results


def extend_instance(instance, *bases, **kwargs):
    """
    Apply subclass (mixin) to a class object or its instance

    By default, the mixin is placed at the start of bases
    to ensure its called first as per MRO. If you wish to
    have it injected last, which is useful for monkeypatching,
    then you can specify 'last=True'. See here:
    http://stackoverflow.com/a/10018792/1267398

    :attr cls: Target object
    :type cls: Class instance

    :attr bases: List of new bases to subclass with

    :attr last: Inject new bases after existing bases
    :type last: bool

    >>> class A(object): pass
    >>> class B(object): pass
    >>> a = A()
    >>> b = B()
    >>> isinstance(b, A)
    False
    >>> extend_instance(b, A)
    >>> isinstance(b, A)
    True
    """
    last = kwargs.get('last', False)
    bases = tuple(bases)
    for base in bases:
        assert inspect.isclass(base), "bases must be classes"
    assert not inspect.isclass(instance)
    base_cls = instance.__class__
    base_cls_name = instance.__class__.__name__
    new_bases = (base_cls,)+bases if last else bases+(base_cls,)
    new_cls = type(base_cls_name, tuple(new_bases), {})
    setattr(instance, '__class__', new_cls)


def extend_class(cls, *bases, **kwargs):
    """
    Add bases to class (late subclassing)

    >>> class A(object): pass
    >>> class B(object): pass
    >>> class C(object): pass
    >>> issubclass(B, A)
    False
    >>> D = extend_class(B, A)
    >>> issubclass(D, A)
    True
    >>> issubclass(D, B)
    True
    """
    last = kwargs.get('last', False)
    bases = tuple(bases)
    for base in bases:
        assert inspect.isclass(base), "bases must be classes"

    new_bases = (cls,)+bases if last else bases+(cls,)
    new_cls = type(cls.__name__, tuple(new_bases), {})
    return new_cls


def import_from_path(path):
    """
    Imports a package, module or attribute from path
    Thanks http://stackoverflow.com/a/14050282/1267398

    >>> import_from_path('os.path')
    <module 'posixpath' ...
    >>> import_from_path('os.path.basename')
    <function basename at ...
    >>> import_from_path('os')
    <module 'os' from ...
    >>> import_from_path('getrektcunt')
    Traceback (most recent call last):
    ImportError:
    >>> import_from_path('os.dummyfunc')
    Traceback (most recent call last):
    ImportError:
    >>> import_from_path('os.dummyfunc.dummylol')
    Traceback (most recent call last):
    ImportError:
    """
    try:
        return importlib.import_module(path)
    except ImportError:
        if '.' not in path:
            raise
        module_name, attr_name = path.rsplit('.', 1)
        if not does_module_exist(module_name):
            raise ImportError("No object found at '{}'".format(path))
        mod = importlib.import_module(module_name)

        if not hasattr(mod, attr_name):
            raise ImportError("No object found at '{}'".format(path))
        return getattr(mod, attr_name)



def does_module_exist(path):
    """
    Check if Python module exists at path

    >>> does_module_exist('os.path')
    True
    >>> does_module_exist('dummy.app')
    False
    """
    try:
        importlib.import_module(path)
        return True
    except ImportError:
        return False


def sort_dict_by_key(obj):
    """
    Sort dict by its keys

    >>> sort_dict_by_key(dict(c=1, b=2, a=3, d=4))
    OrderedDict([('a', 3), ('b', 2), ('c', 1), ('d', 4)])
    """
    sort_func = lambda x: x[0]
    return OrderedDict(sorted(obj.items(), key=sort_func))


def generate_random_token(length=32):
    """
    Generate random secure token

    >>> len(generate_random_token())
    32
    >>> len(generate_random_token(6))
    6
    """
    chars = (string.ascii_lowercase + string.ascii_uppercase + string.digits)
    return ''.join(random.choice(chars) for _ in range(length))


def default(*args, **kwargs):
    """
    Return first argument which is "truthy"

    >>> default(None, None, 1)
    1
    >>> default(None, None, 123)
    123
    >>> print(default(None, None))
    None
    """
    default = kwargs.get('default', None)
    for arg in args:
        if arg:
            return arg
    return default


def urljoin(*args):
    """
    Joins given arguments into a url, removing duplicate slashes
    Thanks http://stackoverflow.com/a/11326230/1267398

    >>> urljoin('/lol', '///lol', '/lol//')
    '/lol/lol/lol'
    """
    value = "/".join(map(lambda x: str(x).strip('/'), args))
    return "/{}".format(value)


def is_hex(value):
    """
    Check if value is hex

    >>> is_hex('abab')
    True
    >>> is_hex('gg')
    False
    """
    try:
        int(value, 16)
    except ValueError:
        return False
    else:
        return True


def is_int(value):
    """
    Check if value is an int

    :type value: int, str, bytes, float, Decimal

    >>> is_int(123), is_int('123'), is_int(Decimal('10'))
    (True, True, True)
    >>> is_int(1.1), is_int('1.1'), is_int(Decimal('10.1'))
    (False, False, False)
    >>> is_int(object)
    Traceback (most recent call last):
    TypeError:
    """
    ensure_type(value, (int, str, bytes, float, Decimal))
    if isinstance(value, int):
        return True
    elif isinstance(value, float):
        return False
    elif isinstance(value, Decimal):
        return str(value).isdigit()
    elif isinstance(value, (str, bytes)):
        return value.isdigit()
    raise ValueError() # pragma: nocover


def padded_split(value, sep, maxsplit=None, pad=None):
    """
    Modified split() to include padding
    See http://code.activestate.com/lists/python-ideas/3366/

    :attr value: see str.split()
    :attr sep: see str.split()
    :attr maxsplit: see str.split()
    :attr pad: Value to use for padding maxsplit

    >>> padded_split('text/html', ';', 1)
    ['text/html', None]
    >>> padded_split('text/html;q=1', ';', 1)
    ['text/html', 'q=1']
    >>> padded_split('text/html;a=1;b=2', ';', 1)
    ['text/html', 'a=1;b=2']
    >>> padded_split('text/html', ';', 1, True)
    ['text/html', True]
    >>> padded_split('text/html;a=1;b=2', ';', 2)
    ['text/html', 'a=1', 'b=2']
    >>> padded_split('text/html;a=1', ';', 2)
    ['text/html', 'a=1', None]
    """
    result = value.split(sep, maxsplit)
    if maxsplit is not None:
        result.extend(
            [pad] * (1+maxsplit-len(result)))
    return result


def coerce_to_bytes(value, encoding='utf-8'):
    """
    Coerce value to bytes

    >>> a = coerce_to_bytes('hello')
    >>> b = coerce_to_bytes(b'hello')
    >>> if six.PY2: assert isinstance(a, str)
    >>> if six.PY2: assert isinstance(b, str)
    >>> if six.PY3: assert isinstance(a, bytes)
    >>> if six.PY3: assert isinstance(b, bytes)
    """
    ensure_type(value, (bytes, str))
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode(encoding)


class Tempfile(object):
    """
    Tempfile wrapper with cleanup support

    XXX: Needs UT
    """

    def __init__(self):
        self.paths = []

    def mkstemp(self, *args, **kwargs):
        path = tempfile.mkstemp(*args, **kwargs)
        self.paths.append(path)
        return path

    def mkdtemp(self, *args, **kwargs):
        path = tempfile.mkdtemp(*args, **kwargs)
        self.paths.append(path)
        return path

    def cleanup(self):
        """Remove any created temp paths"""
        for path in self.paths:
            if isinstance(path, tuple):
                os.close(path[0])
                os.unlink(path[1])
            else:
                shutil.rmtree(path)
        self.paths = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

