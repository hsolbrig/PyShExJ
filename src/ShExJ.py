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
from typing import Optional, Dict, List
from jsg import JSGString, JSGPattern, JSGSchema, JSGObject, bind, Union


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


@bind(JSGSchema(include=shapeLabel))
class Inclusion(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.include: shapeLabel = None


@bind(JSGSchema(length=Optional[INTEGER],
                minlength=Optional[INTEGER],
                maxlength=Optional[INTEGER],
                pattern=Optional[STRING]))
class stringFacet(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.length: Optional[INTEGER] = None
        self.minlength: Optional[INTEGER] = None
        self.maxlength: Optional[INTEGER] = None
        self.pattern: Optional[STRING] = None


@bind(JSGSchema(mininclusive=Optional[numericLiteral],
                minexclusive=Optional[numericLiteral],
                maxinclusive=Optional[numericLiteral],
                maxexclusive=Optional[numericLiteral],
                totaldigits=Optional[INTEGER],
                fractiondigits=Optional[INTEGER]))
class numericFacet(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.mininclusive: Optional[numericLiteral] = None
        self.minexclusive: Optional[numericLiteral] = None
        self.maxinclusive: Optional[numericLiteral] = None
        self.maxexclusive: Optional[numericLiteral] = None
        self.totaldigits: Optional[INTEGER] = None
        self.fractiondigits: Optional[INTEGER] = None

xsFacet = Union[stringFacet, numericFacet]


@bind(JSGSchema(stem=IRI))
class Stem(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.stem: IRI = None


@bind()
class Wildcard(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)


@bind(JSGSchema(stem=Union[IRI, Wildcard],
                exclusions=Optional[List[Union[objectValue, Stem]]]))
class StemRange(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.stem: Union[IRI, Wildcard] = None
        self.exclusions: Optional[List[Union[objectValue, Stem]]] = None

valueSetValue = Union[objectValue, Stem, StemRange]


@bind(JSGSchema(name=IRI,
                code=Optional[STRING]))
class SemAct(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.name: IRI = None
        self.code: objectValue = None


@bind(JSGSchema(predicate=IRI,
                object=objectValue))
class Annotation(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.predicate: IRI = None
        self.object: objectValue = None


@bind(JSGSchema(inverse=Optional[BOOL],
                negated=Optional[BOOL],
                predicate=IRI,
                # valueExpr=Optional[shapeExpr],
                min=Optional[INTEGER],
                max=Optional[Union[INTEGER, STAR]],
                semActs=Optional[List[SemAct]],
                annotations=Optional[List[Annotation]]))
class TripleConstraint(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.inverse: Optional[BOOL] = None
        self.negated: Optional[BOOL] = None
        self.predicate: IRI = None
        self.valueExpr: Optional[shapeExpr] = None
        self.min: Optional[INTEGER] = None
        self.max: Optional[Union[INTEGER, STAR]] = None
        self.semActs: Optional[List[SemAct]] = None
        self.annotations: Optional[List[Annotation]] = None


@bind(JSGSchema(min=Optional[INTEGER],
                max=Optional[Union[INTEGER, STAR]],
                semActs=Optional[List[SemAct]],
                annotations=Optional[List[Annotation]]))
class OneOf(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.expressions: List[tripleExpr] = None
        self.min: Optional[INTEGER] = None
        self.max: Optional[Union[INTEGER, STAR]] = None
        self.semActs: Optional[List[SemAct]] = None
        self.annotations: Optional[List[Annotation]] = None


@bind(JSGSchema(min=Optional[INTEGER],
                max=Optional[Union[INTEGER, STAR]],
                semActs=Optional[List[SemAct]],
                annotations=Optional[List[Annotation]]))
class EachOf(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.expressions: List[tripleExpr] = None
        self.min: Optional[INTEGER] = None
        self.max: Optional[Union[INTEGER, STAR]] = None
        self.semActs: Optional[List[SemAct]] = None
        self.annotations: Optional[List[Annotation]] = None


tripleExpr = Union[EachOf, OneOf, TripleConstraint, Inclusion]

OneOf._add_to_schema(expressions=List[tripleExpr])
EachOf._add_to_schema(expressions=List[tripleExpr])


@bind()
class ShapeExternal(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)


@bind(JSGSchema(reference=IRI))
class ShapeRef(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.reference: IRI = None


@bind(JSGSchema(virtual=Optional[BOOL],
                closed=Optional[BOOL],
                extra=Optional[List[IRI]],
                expression=Optional[tripleExpr],
                inherit=Optional[List[shapeLabel]],
                semActs=Optional[List[SemAct]]))
class Shape(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.virtual: Optional[BOOL] = None
        self.closed: Optional[BOOL] = None
        self.extra: Optional[List[IRI]] = None
        self.expression: Optional[tripleExpr] = None
        self.inherit: Optional[List[shapeLabel]] = None
        self.semActs: Optional[List[SemAct]] = None


class NodeType(JSGString):
    pattern = JSGPattern(r'iri|bnode|nonliteral|literal')


@bind(JSGSchema(nodeKind=Optional[NodeType],
                datatype=Optional[IRI],
                values=Optional[List[valueSetValue]],
                **stringFacet._schema,
                **numericFacet._schema))
class NodeConstraint(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.nodeKind: Optional[NodeType] = None
        self.datatype: Optional[IRI] = None
        self.mininclusive: Optional[numericLiteral] = None
        self.minexclusive: Optional[numericLiteral] = None
        self.maxinclusive: Optional[numericLiteral] = None
        self.maxexclusive: Optional[numericLiteral] = None
        self.totaldigits: Optional[INTEGER] = None
        self.fractiondigits: Optional[INTEGER] = None
        self.length: Optional[INTEGER] = None
        self.minlength: Optional[INTEGER] = None
        self.maxlength: Optional[INTEGER] = None
        self.pattern: Optional[STRING] = None
        self.values: Optional[List[valueSetValue]] = None


@bind()
class ShapeNot(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.shapeExpr: shapeExpr = None


@bind()
class ShapeAnd(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.shapeExprs: List[shapeExpr] = None


@bind()
class ShapeOr(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.shapeExprs: List[shapeExpr] = None


shapeExpr = Union[ShapeOr, ShapeAnd, ShapeNot, NodeConstraint, Shape, ShapeRef, ShapeExternal]

ShapeNot._add_to_schema(shapeExpr=shapeExpr)
ShapeAnd._add_to_schema(shapeExprs=List[shapeExpr])
ShapeOr._add_to_schema(shapeExprs=List[shapeExpr])
TripleConstraint._add_to_schema(valueExpr=Optional[shapeExpr])


@bind(JSGSchema(prefixes=Optional[Dict[PREFIX, IRI]],
                base=Optional[IRI],
                startActs=Optional[List[SemAct]],
                start=Optional[shapeExpr],
                shapes=Optional[Dict[shapeLabel, shapeExpr]]))
class Schema(JSGObject):

    def __init__(self):
        JSGObject.__init__(self)
        self.prefixes: Optional[Dict[PREFIX, IRI]] = None
        self.base: Optional[IRI] = None
        self.startActs: Optional[List[SemAct]] = None
        self.start: Optional[shapeExpr] = None
        self.shapes: Optional[Dict[shapeLabel, shapeExpr]] = None
