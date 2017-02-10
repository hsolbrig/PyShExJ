# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import re
import json
from jsonasobj import JsonObj
from logger import Logger
from numbers import Number

from typing import Dict, Optional, TextIO, Union, List, Set, Type

from collections import Iterable

# Map from jsg TYPE to corresponding class
schemaMap = {}          # type: Dict[str, Type[JSGObject]]

# JSG type entry
# TODO: Figure out how to load these from the compiled JSG
TYPE = "type"           # type: str
IGNORE = []             # type: List[str]   List of properties to globally ignore

# TODO: Extend List to include a minimum and maximum value


class JSGObject(JsonObj):
    """
    JSGObject is a JsonObj with constraints.

    Note that methods and variables in JSGObject should always begin with "_", as we currently restrict the set of
    JSON names to those that begin with [a-zA-Z]
    """

    @staticmethod
    def _strip_nones(obj):
        """
        An attribute with type None is equivalent to an absent attribute.
        :param obj: Object with attributes
        :return: Object dictionary w/ Nones and underscores stripped
        """
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_") and v is not None}

    def _default(self, obj):
        """ a function that returns a serializable version of obj. Overrides JsonObj method
        :param obj: Object to be serialized
        :return: Serialized version of obj
        """
        return JSGObject._strip_nones(obj) if isinstance(obj, JsonObj)\
            else str(obj) if isinstance(obj, JSGString) else json.JSONEncoder().default(obj)


class JSGPattern:
    """
    JSG Parsing pattern
    """
    def __init__(self, pattern: str):
        """
        Compile and record a match pattern
        :param pattern:
        """
        self.pattern = re.compile(pattern)

    def matches(self, txt: str) -> bool:
        """
        Determine whether txt matches pattern
        :param txt: text to check
        :return: True if match
        """
        match = self.pattern.match(txt)
        return match and match.endpos == len(txt)


class JSGString:
    pattern = None          # type: JSGPattern

    def __init__(self, val: str):
        """
        Construct a simple string variable
        :param val: string
        """
        self.val = val

    @classmethod
    def _test_valid(cls, val: str) -> bool:
        return not cls.pattern or cls.pattern.matches(val)

    def _is_valid(self, log: Logger) -> bool:
        """
        Determine whether the string is valid
        :param log: function for reporting the result
        :return: Result
        """
        if not isinstance(self.val, str):
            log.log("Wrong type for {}. Expected: {} Actual: {}"
                    .format(self.__class__.__name__, type(str), type(self.val)))
            return False
        if self.pattern:
            if self.pattern.matches(self.val):
                return True
            log.log("Wrong type: {}: {}".format(self.__class__.__name__, self.val))
            return False
        return True

    def __str__(self):
        return self.val

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.val == other.val
        elif isinstance(other, str):
            return self.val == other
        return False

    def __hash__(self):
        return hash(self.val)


class JSGSchema:
    """
    A JSON Schema Grammar (JSG) instance
    """

    def __init__(self, **schema):
        """
        Construct a JSG Schema instance
        :param schema: dictionary of name/type tuples
        """
        self.schema = schema            # type: Dict[str, object]

    @staticmethod
    def _test(entry, log: Logger) -> bool:
        """
        Test whether entry conforms
        :param entry:
        :param log:
        :return:
        """
        if isinstance(entry, dict):
            for k, v in entry.items():
                if callable(getattr(k, "_is_valid", None)) and not k._is_valid(log) and log.log():
                    return True
                if callable(getattr(v, "_is_valid", None)) and not v._is_valid(log) and log.log():
                    return True
        elif isinstance(entry, list):
            for v in entry:
                if callable(getattr(v, "_is_valid", None)) and not v._is_valid(log) and log.log():
                    return True
        elif isinstance(entry, (JSGObject, JSGString)):
            if not entry._is_valid(log) and log.log():
                return True
        else:
            raise TypeError("Unhandled type")
        return False

    def conforms(self, instance: object, log: Logger, strict: bool = True) -> bool:
        """
        Determine whether the supplied instance conforms to this Schema
        :param instance: Object to test
        :param log: Output for logging non-conformance messages.
        :param strict: True means that extra fields are not allowed
        :return: True if conforms
        """
        nerrors = log.nerrors

        # Test each schema entry against object
        for name, typ in self.schema.items():
            entry = instance.__dict__.get(name)            # Note: None and absent are equivalent
            if entry is None:
                if not issubclass(type(None), typ) and log.log("Missing required element: {}: {}".format(name, typ)):
                    return False
            elif not issubclass(type(entry), typ):
                if log.log("Type mismatch for {}. Expecting: {} Got: {}".format(name, typ, type(entry))):
                    return False
            elif self._test(entry, log):                    # Make sure that entry conforms to its type
                    return False

        if strict:
            # Test each attribute against the schema
            for k, v in instance.__dict__.items():
                if not k.startswith("_") and k not in self.schema and k != TYPE and k not in IGNORE:
                    if log.log("Extra element: {}: {}".format(k, v)):
                        return False

        return log.nerrors == nerrors


def type_instance(typ, instance) -> object:
    """
    Return a correctly typed instance
    :param typ: expected type
    :param instance: instance
    :return: correctly typed instance
    """
    if instance is None:
        return instance
    elif issubclass(type(instance), typ):       # Already correctly typed
        return instance
    elif issubclass(typ, JSGString) and isinstance(instance, (str, Number)) and typ._test_valid(str(instance)):
        return typ(str(instance))
    elif issubclass(typ, Dict):
        if isinstance(instance, dict):
            return instance
        else:
            raise TypeError("{} cannot be converted to a dictionary".format(instance))
    elif issubclass(typ, List):
        return list(instance if isinstance(instance, Iterable) else [instance])
    elif issubclass(typ, Set):
        return instance if isinstance(instance, set) else set(instance)
    elif issubclass(typ, Union):
        for union_type in typ.__union_params__:
            ti = type_instance(union_type, instance)
            if ti is not None:
                return ti

    return None


def bind(schema: JSGSchema = None):
    """
    Bind a JSGObject to a JSG Schema
    :param schema: schema to bind to object.  If not supplied, an empty schema is used
    :return: Wrapper class
    """
    if schema is None:
        schema = JSGSchema()

    def wrapper(cls: Type[JSGObject]) -> object:
        cls._schema = schema

        class WrapperClass(cls):
            def __init__(self, **kwargs):
                cls.__init__(self)
                if TYPE:
                    setattr(self, TYPE, cls.__name__)
                self._load(**kwargs)

            @staticmethod
            def _add_to_schema(**kwargs) -> None:
                """
                Add kwargs to the schema.  Used for resolving circular references
                :param kwargs: entries to append to the schema
                """
                for k, v in kwargs.items():
                    cls._schema.schema[k] = v

            @staticmethod
            def _get_schema() -> JSGSchema:
                return cls._schema

            def _load(self, **kwargs):
                for name in kwargs:
                    if name in self._get_schema().schema:
                        setattr(self, name, type_instance(self._get_schema().schema[name], kwargs[name]))
                    else:
                        setattr(self, name, kwargs[name])

            def _is_valid(self, log: Optional[Logger] = None) -> bool:
                if log is None:
                    log = Logger()
                if getattr(self, TYPE) != cls.__name__:
                    if log.log("Type mismatch - Expected: {} Actual: {}".format(cls.__name__, getattr(self, TYPE))):
                        return False
                return cls._schema.conforms(self, log)

            @property
            def _cls(self) -> object:
                return cls

            def __repr__(self):
                return "bind.WrapperClass({})".format(cls)

        schemaMap[cls.__name__] = WrapperClass
        return WrapperClass
    return wrapper


def loads_loader(pairs) -> object:
    if TYPE in pairs:
        cls = schemaMap.get(pairs[TYPE])
        if cls:
            return cls(**pairs)
        raise Exception("Unknown type: {}".format(pairs[TYPE]))
    return pairs


def loads(s: str, **kwargs) -> JSGObject:
    """ Convert a json_str into a JSGObject instance
    :param s: a str instance containing a JSON document
    :param kwargs: arguments see: json.load for details
    :return: JsonObj representing the json string
    """
    return json.loads(s, object_hook=loads_loader, **kwargs)


def load(fp: TextIO, **kwargs) -> JSGObject:
    """ Deserialize fp (a .read()-supporting file-like object containing a JSON document) to a JsonObj
    :param fp: file-like object to deserialize
    :param kwargs: arguments. see: json.load for details
    :return: JsonObj representing fp
    """
    return loads(fp.read(), **kwargs)
