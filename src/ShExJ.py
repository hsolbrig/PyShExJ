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
from typing import Optional, Dict, List, Union, _ForwardRef
from jsg import JSGString, JSGPattern, JSGObject
from typing_patch import fix_forwards


class LANGTAG(JSGString):
    pattern = JSGPattern(r'@[a-zA-Z]+(-[a-zA-Z0-9]+)*')


class EXPONENT(JSGString):
    pattern = JSGPattern(r'[eE][+=]?[0-9]+')


class HEX(JSGString):
    pattern = JSGPattern(r'[0-9A-Fa-f]')


class UCHAR(JSGString):
    pattern = JSGPattern(r'\\u{HEX}{HEX}{HEX}{HEX}|\\U{HEX}{HEX}{HEX}{HEX}{HEX}{HEX}{HEX}{HEX}'.format(HEX=HEX.pattern))


class PN_CHARS_BASE(JSGString):
    pattern = JSGPattern(r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D'
                         r'\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\u10000-\uEFFFF]')


class PN_CHARS_U(JSGString):
    pattern = JSGPattern(r'{PN_CHARS_BASE}|_'.format(PN_CHARS_BASE=PN_CHARS_BASE.pattern))


class PN_CHARS(JSGString):
    pattern = JSGPattern(r'{PN_CHARS_U} | [\-0-9\u00B7\u0300-\u036F\u203F-\u2040]'
                         .format(PN_CHARS_U=PN_CHARS_U.pattern))


class PN_PREFIX(JSGString):
    pattern = JSGPattern(r'{PN_CHARS_BASE}(({PN_CHARS}|\.)*{PN_CHARS})?'.format(PN_CHARS_BASE=PN_CHARS_BASE.pattern,
                                                                                PN_CHARS=PN_CHARS.pattern))


class PREFIX(JSGString):
    pattern = JSGPattern(r'({PN_PREFIX})?'.format(PN_PREFIX=PN_PREFIX.pattern))


class IRI(JSGString):
    pattern = JSGPattern(r'({PN_CHARS}|[.:/\\#@%&]|{UCHAR})*'.format(PN_CHARS=PN_CHARS.pattern, UCHAR=UCHAR.pattern))


class BNODE(JSGString):
    pattern = JSGPattern(r'_:({PN_CHARS_U}|[0-9])(({PN_CHARS}|\.)*{PN_CHARS})?'.format(PN_CHARS=PN_CHARS.pattern,
                                                                                       PN_CHARS_U=PN_CHARS_U.pattern))


class BOOL(JSGString):
    pattern = JSGPattern(r'true|false')


class INTEGER(JSGString):
    pattern = JSGPattern(r'[+-]?[0-9]+')


class DECIMAL(JSGString):
    pattern = JSGPattern(r'[+-]?[0-9]*\.[0-9]+')


class DOUBLE(JSGString):
    pattern = JSGPattern(r'[+-]?([0-9]+\.[0-9]*{EXPONENT}|\.[0-9]+{EXPONENT})'.format(EXPONENT=EXPONENT.pattern))


class SIMPLE_LITERAL(JSGString):
    pattern = JSGPattern(r'"([^"\r\n]|\\")*"')


class DATATYPE_LITERAL(JSGString):
    pattern = JSGPattern(r'{SIMPLE_LITERAL}^^{IRI}'.format(SIMPLE_LITERAL=SIMPLE_LITERAL.pattern, IRI=IRI.pattern))


class LANG_LITERAL(JSGString):
    pattern = JSGPattern(r'{SIMPLE_LITERAL}{LANGTAG}'.format(SIMPLE_LITERAL=SIMPLE_LITERAL.pattern,
                                                             LANGTAG=LANGTAG.pattern))


class STRING(JSGString):
    pattern = JSGPattern(r'.*')


class STAR(JSGString):
    pattern = JSGPattern(r'\*')

RDFLiteral = Union[SIMPLE_LITERAL, DATATYPE_LITERAL, LANG_LITERAL]
numericLiteral = Union[INTEGER, DECIMAL, DOUBLE]
shapeLabel = Union[IRI, BNODE]

objectValue = Union[IRI, RDFLiteral]

shapeExprT = _ForwardRef('shapeExpr')
tripleExprT = _ForwardRef('tripleExpr')


class Inclusion(JSGObject):

    def __init__(self,
                 include: shapeLabel,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.include = include


class stringFacet(JSGObject):

    def __init__(self,
                 length: Optional[INTEGER] = None,
                 minlength: Optional[INTEGER] = None,
                 maxlength: Optional[INTEGER] = None,
                 pattern: Optional[STRING] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.length = length
        self.minlength = minlength
        self.maxlength = maxlength
        self.pattern = pattern


class numericFacet(JSGObject):

    def __init__(self,
                 mininclusive: Optional[numericLiteral] = None,
                 minexclusive: Optional[numericLiteral] = None,
                 maxinclusive: Optional[numericLiteral] = None,
                 maxexclusive: Optional[numericLiteral] = None,
                 totaldigits: Optional[INTEGER] = None,
                 fractiondigits: Optional[INTEGER] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.mininclusive = mininclusive 
        self.minexclusive = minexclusive 
        self.maxinclusive = maxinclusive 
        self.maxexclusive = maxexclusive 
        self.totaldigits = totaldigits 
        self.fractiondigits = fractiondigits

xsFacet = Union[stringFacet, numericFacet]


class Stem(JSGObject):

    def __init__(self,
                 stem: IRI,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.stem = stem


class Wildcard(JSGObject):

    def __init__(self,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)


class StemRange(JSGObject):

    def __init__(self,
                 stem: Union[IRI, Wildcard],
                 exclusions: Optional[List[Union[objectValue, Stem]]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.stem = stem
        self.exclusions = exclusions

valueSetValue = Union[objectValue, Stem, StemRange]


class SemAct(JSGObject):

    def __init__(self,
                 name: IRI,
                 code: Optional[STRING] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.name = name
        self.code = code


class Annotation(JSGObject):

    def __init__(self,
                 predicate: IRI,
                 object: objectValue,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.predicate = predicate
        self.object = object


class TripleConstraint(JSGObject):

    def __init__(self,
                 predicate: IRI,
                 inverse: Optional[BOOL]= None,
                 negated: Optional[BOOL]= None,
                 valueExpr: Optional[shapeExprT]= None,
                 min: Optional[INTEGER]= None,
                 max: Optional[Union[INTEGER, STAR]]= None,
                 semActs: Optional[List[SemAct]]= None,
                 annotations: Optional[List[Annotation]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.predicate = predicate
        self.inverse = inverse
        self.negated = negated
        self.valueExpr: Optional[shapeExpr] = valueExpr
        self.min = min
        self.max = max
        self.semActs = semActs
        self.annotations = annotations


class OneOf(JSGObject):

    def __init__(self,
                 expressions: List[tripleExprT],
                 min: Optional[INTEGER] = None,
                 max: Optional[Union[INTEGER, STAR]] = None,
                 semActs: Optional[List[SemAct]] = None,
                 annotations: Optional[List[Annotation]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.expressions = expressions
        self.min = min
        self.max = max
        self.semActs = semActs
        self.annotations = annotations


class EachOf(JSGObject):

    def __init__(self,
                 expressions: List[tripleExprT],
                 min: Optional[INTEGER] = None,
                 max: Optional[Union[INTEGER, STAR]] = None,
                 semActs: Optional[List[SemAct]] = None,
                 annotations: Optional[List[Annotation]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.expressions = expressions
        self.min = min
        self.max = max
        self.semActs = semActs
        self.annotations = annotations


tripleExpr = Union[EachOf, OneOf, TripleConstraint, Inclusion]


class ShapeExternal(JSGObject):

    def __init__(self, **_: Dict[str, object]):
        JSGObject.__init__(self)


class ShapeRef(JSGObject):

    def __init__(self,
                 reference: IRI,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.reference = reference


class Shape(JSGObject):

    def __init__(self,
                 virtual: Optional[BOOL] = None,
                 closed: Optional[BOOL] = None,
                 extra: Optional[List[IRI]] = None,
                 expression: Optional[tripleExpr] = None,
                 inherit: Optional[List[shapeLabel]] = None,
                 semActs: Optional[List[SemAct]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.virtual = virtual
        self.closed = closed
        self.extra = extra
        self.expression = expression
        self.inherit = inherit
        self.semActs = semActs


class NodeType(JSGString):
    pattern = JSGPattern(r'iri|bnode|nonliteral|literal')


class NodeConstraint(JSGObject):

    def __init__(self,
                 nodeKind: Optional[NodeType] = None,
                 datatype: Optional[IRI] = None,
                 mininclusive: Optional[numericLiteral] = None,
                 minexclusive: Optional[numericLiteral] = None,
                 maxinclusive: Optional[numericLiteral] = None,
                 maxexclusive: Optional[numericLiteral] = None,
                 totaldigits: Optional[INTEGER] = None,
                 fractiondigits: Optional[INTEGER] = None,
                 length: Optional[INTEGER] = None,
                 minlength: Optional[INTEGER] = None,
                 maxlength: Optional[INTEGER] = None,
                 pattern: Optional[STRING] = None,
                 values: Optional[List[valueSetValue]] = None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.nodeKind = nodeKind
        self.datatype = datatype
        self.mininclusive = mininclusive
        self.minexclusive = minexclusive
        self.maxinclusive = maxinclusive
        self.maxexclusive = maxexclusive
        self.totaldigits = totaldigits
        self.fractiondigits = fractiondigits
        self.length = length
        self.minlength = minlength
        self.maxlength = maxlength
        self.pattern = pattern
        self.values = values


class ShapeNot(JSGObject):

    def __init__(self,
                 shapeExpr: shapeExprT,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.shapeExpr = shapeExpr


class ShapeAnd(JSGObject):

    def __init__(self,
                 shapeExprs: List[shapeExprT],
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.shapeExprs = shapeExprs


class ShapeOr(JSGObject):

    def __init__(self,
                 shapeExprs: List[shapeExprT],
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.shapeExprs = shapeExprs

shapeExpr = Union[ShapeOr, ShapeAnd, ShapeNot, NodeConstraint, Shape, ShapeRef, ShapeExternal]


class Schema(JSGObject):

    def __init__(self,
                 prefixes: Optional[Dict[PREFIX, IRI]]=None,
                 base: Optional[IRI]=None,
                 startActs: Optional[List[SemAct]]=None,
                 start: Optional[shapeExpr]=None,
                 shapes: Optional[Dict[shapeLabel, shapeExpr]]=None,
                 **_: Dict[str, object]):
        JSGObject.__init__(self)
        self.prefixes = prefixes
        self.base = base
        self.startActs = startActs
        self.start = start
        self.shapes = shapes


fix_forwards(globals())
