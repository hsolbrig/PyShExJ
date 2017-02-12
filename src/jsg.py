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
from typing import Dict, TextIO, Union, Optional

from typing_patch import conforms, as_type, is_typing_type

# Map from jsg TYPE to corresponding class
schemaMap: Dict[str, object] = {}

# JSG type entry
# TODO: Figure out how to load these from the compiled JSG
TYPE = "type"           # type: str
IGNORE = []             # type: List[str]   List of properties to globally ignore

# TODO: Extend List to include a minimum and maximum value


class JSGValidateable:
    def _is_valid(self, log: Optional[Logger] = None) -> bool:
        """
        Mixin for
        :param log: Logger to record reason for non validation.
        :return: True if valid, false otherwise
        """
        log.log("Unimplemented validate function")
        return False

    @property
    def _class_name(self):
        return type(self).__name__


class JSGObject(JsonObj, JSGValidateable):
    """
    JSGObject is a JsonObj with constraints.

    Note that methods and variables in JSGObject should always begin with "_", as we currently restrict the set of
    JSON names to those that begin with [a-zA-Z]
    """
    _schema = None

    def __init__(self, **_):
        """
        Initialization is actually handled in bind Wrapper class.  This method exists for type checking
        :param _: Dict
        """
        JsonObj.__init__(self)
        pass

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

    def _is_valid(self, log: Optional[Logger] = None) -> bool:
        if not log:
            log = Logger()
        if getattr(self, TYPE) != self._class_name:
            if log.log("Type mismatch - Expected: {} Actual: {}".format(self._class_name, getattr(self, TYPE))):
                return False
        return self._schema.conforms(self, log)


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
        if not isinstance(txt, str):
            print("HERE")
        match = self.pattern.match(txt)
        return match and match.endpos == len(txt)


class JSGStringMeta(type):

    def __instancecheck__(self, instance) -> bool:
        # TODO: This is too loose - we really need to see whether instance is the same class as us
        return not self.pattern or self.pattern.matches(str(instance).lower()
                                                        if isinstance(instance, bool) else str(instance))


class JSGString(JSGValidateable, metaclass=JSGStringMeta):
    """
    A string with an optional parsing pattern
    """
    pattern = None          # type: JSGPattern

    def __init__(self, val: str):
        """
        Construct a simple string variable
        :param val: string
        """
        self.val = val

    def _is_valid(self, log: Optional[Logger] = None) -> bool:
        """
        Determine whether the string is valid
        :param log: function for reporting the result
        :return: Result
        """
        if not log:
            log = Logger()
        if not isinstance(self.val, str):
            log.log("Wrong type for {}. Expected: {} Actual: {}"
                    .format(self._class_name, type(str), type(self.val)))
            return False
        if self.pattern:
            if self.pattern.matches(self.val):
                return True
            log.log("Wrong type: {}: {}".format(self._class_name, self.val))
            return False
        return True

    def __str__(self):
        return self.val

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.val == str(other)
        return False

    def __hash__(self):
        return hash(self.val)


class JSGSchema(dict):
    """
    A JSON Schema Grammar (JSG) instance
    """

    @staticmethod
    def _test(entry, log: Logger) -> bool:
        """
        Test whether entry conforms to its type
        :param entry: entry to test
        :param log: place to record issues
        :return: True if it meets requirements
        """
        if isinstance(entry, dict):
            for k, v in entry.items():
                if isinstance(k, JSGValidateable) and not k._is_valid(log) and not log.logging:
                    return False
                if isinstance(v, JSGValidateable) and not v._is_valid(log) and not log.logging:
                    return False
        elif isinstance(entry, list):
            for v in entry:
                if isinstance(v, JSGValidateable) and not v._is_valid(log) and not log.logging:
                    return False
        elif isinstance(entry, JSGValidateable):
            if not entry._is_valid(log) and not log.logging:
                return False
        return True

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
        for name, typ in self.items():
            entry = instance.__dict__.get(name)               # Note: None and absent are equivalent
            if not conforms(entry, typ):
                if entry is None:
                    if log.log("{}: Missing required field: {}".format(type(self).__name__, name)):
                        return False
                else:
                    if log.log("{}: Type mismatch for {}. Expecting: {} Got: {}"
                               .format(type(self).__name__, name, typ, type(entry))):
                        return False
            elif entry is not None and not self._test(entry, log):    # Make sure that entry conforms to its own type
                return False

        if strict:
            # Test each attribute against the schema
            for k, v in instance.__dict__.items():
                if not k.startswith("_") and k not in self and k != TYPE and k not in IGNORE:
                    if log.log("Extra element: {}: {}".format(k, v)):
                        return False

        return log.nerrors == nerrors


def type_instance(typ, instance) -> object:
    """
    Cooerce instance to type if possible.
    :param typ: expected type
    :param instance: instance
    :return: correctly typed instance or None if not possible.  (Note that None returns None as well)
    """
    if instance is None:                        # None == absent
        return instance

    typed_instance = as_type(instance, typ)
    if typed_instance is not None:
        return typed_instance
    if is_typing_type(typ):
        return None
    return typ(str(instance))


def bind(schema: JSGSchema = None):
    """
    Bind a JSGObject to a JSG Schema
    :param schema: schema to bind to object.  If not supplied, an empty schema is used
    :return: Wrapper for actual class.
    """
    if schema is None:
        schema = JSGSchema()

    def wrapper(cls: JSGObject) -> object:
        """
        Class wrapper -- wrap cls in a WrapperClass instance
        :param cls: class to wrap
        :return: WrapperClass
        """
        cls._schema = schema

        class WrapperClass(cls):
            def __init__(self, **kwargs):
                JSGObject.__init__(self)                  # Strictly for type checking
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
                    schema[k] = v

            def _load(self, **kwargs: Dict[str, object]) -> None:
                """
                Load kwargs as variables
                :param kwargs:
                """
                for name in kwargs:
                    if name in schema:
                        setattr(self, name, type_instance(schema[name], kwargs[name]))
                    else:
                        setattr(self, name, kwargs[name])

            @property
            def _class_name(self):
                return cls.__name__

            @property
            def _cls(self) -> object:
                return cls

            def __repr__(self):
                return "bind.WrapperClass({})".format(cls)

        schemaMap[cls.__name__] = WrapperClass
        return WrapperClass
    return wrapper


def loads_loader(pairs) -> object:
    """
    json loader objecthook
    :param pairs:
    :return:
    """
    if TYPE in pairs:
        cls = schemaMap.get(pairs[TYPE])
        if cls:
            return cls(**pairs)
        raise Exception("Unknown type: {}".format(pairs[TYPE]))
    return pairs


def loads(s: str, **kwargs) -> JSGObject:
    """ Convert a JSON string into a JSGObject
    :param s: string representation of JSON document
    :param kwargs: arguments see: json.load for details
    :return: JSGObject representing the json string
    """
    return json.loads(s, object_hook=loads_loader, **kwargs)


def load(fp: Union[TextIO, str], **kwargs) -> JSGObject:
    """ Convert a file name or file-like object containing stringified JSON into a JSGObject
    :param fp: file-like object to deserialize
    :param kwargs: arguments. see: json.load for details
    :return: JSGObject representing fp
    """
    if isinstance(fp, str):
        with open(fp) as f:
            return loads(f.read(), **kwargs)
    else:
        return loads(fp.read(), **kwargs)
