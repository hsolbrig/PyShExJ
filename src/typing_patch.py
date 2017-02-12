# Copyright (c) 2016, Mayo Clinic
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
from typing import _Union, GenericMeta
from collections import Iterable


# TODO: Pay attention to the goings on at the python development (http://bugs.python.org/issue29262) and #377

def conforms(element, typ) -> bool:
    if is_union(typ):
        return union_conforms(element, typ)
    elif is_dict(typ):
        return dict_conforms(element, typ)
    elif is_iterable(typ):
        return iterable_conforms(element, typ)
    else:
        return element_conforms(element, typ)


def is_typing_type(typ) -> bool:
    return is_union(typ) or is_dict(typ) or is_iterable(typ)


def as_type(element, typ) -> object:
    if element is None:
        return element
    if is_union(typ):
        if union_conforms(element, typ):
            return as_union(element, typ)
    elif is_dict(typ):
        if dict_conforms(element, typ):
            return element
    elif is_iterable(typ):
        if iterable_conforms(element, typ):
            return typ.__extra__(element)
    elif element_conforms(element, typ):
        return typ(element)
    return None


def is_union(typ) -> bool:
    return type(typ) is _Union


def is_dict(typ) -> bool:
    return type(typ) is GenericMeta and typ.__extra__ is dict


def is_iterable(typ) -> bool:
    return type(typ) is GenericMeta and issubclass(typ.__extra__, Iterable)


def union_conforms(element, typ) -> bool:
    if is_union(typ):
        return any([conforms(element, t) for t in typ.__args__])
    return False


def as_union(element, typ) -> bool:
    for t in typ.__args__:
        if conforms(element, t):
            return element
    return None


def dict_conforms(element, typ) -> bool:
    if is_dict(typ) and isinstance(element, dict):
        kt, vt = typ.__args__
        return all([conforms(k, kt) and conforms(v, vt) for k, v in element.items()])
    return False


def iterable_conforms(element, typ) -> bool:
    if is_iterable(typ) and isinstance(element, Iterable):
        vt = typ.__args__[0]
        return all([conforms(e, vt) for e in element])
    return False


def element_conforms(element, typ) -> bool:
    if typ is type(None):
        return element is None
    elif element is None:
        return False
    return isinstance(element, typ)
