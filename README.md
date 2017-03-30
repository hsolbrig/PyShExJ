# PyShExJ - python bindings and parser for [ShExJ](https://github.com/shexSpec/shexTest/blob/master/doc/ShExJ.jsg)

# NOTE: This project has been superceded by the [PyJSG](http://github.com/hsolbrig/pyjsg) project, which incorporates a JSG to Python compiler.

A collection of Python classes that represent the [json-grammar](https://github.com/ericprud/jsg) definition of the Shape Expressions [ShEx]() language. 

At the moment, [ShExJ.py](src/ShExj.py) has been hand compiled form the [ShExJ.jsg]((https://github.com/shexSpec/shexTest/blob/master/doc/ShExJ.jsg)) source.  Our eventual goal is to create a generic [JSG](https://github.com/ericprud/jsg) compiler that will generate the equivalent for any JSON schema.

Also note that the ShEx and ShExJ specifications continue to evolve :unamused:, and is difficult to remain 100% current.  We plan to update this package when (if?) the ShEx community finally relases a stable specification.

## Example
```python
import ShExJ
from jsg import loads

shexj = """{
  "type": "Schema",
  "shapes":{
    "http://a.example/S1": {
      "type": "Shape",
      "expression": {
        "type": "TripleConstraint",
        "predicate": "http://a.example/p1",
        "valueExpr": { "type": "NodeConstraint", "datatype": "http://a.example/dt1" }
      }
    }
  }
}"""
s: ShExJ.Schema = loads(shexj, ShExJ)
print("type(Shema): {}".format(s.type))
S1 = ShExJ.IRI("http://a.example/S1")
print("PREDICATE: {}".format(s.shapes[S1].expression.predicate))
s.shapes[S1].closed = ShExJ.BOOL("true")
print(s._as_json_dumps())
print("Valid: {}".format(s._is_valid()))
try:
    s.shapes[S1].clown = ShExJ.INTEGER("17")
except ValueError as e:
    print("No clowns")
```
```text
type(Shema): Schema
PREDICATE: http://a.example/p1
{
   "type": "Schema",
   "shapes": {
      "http://a.example/S1": {
         "type": "Shape",
         "closed": "true",
         "expression": {
            "type": "TripleConstraint",
            "predicate": "http://a.example/p1",
            "valueExpr": {
               "type": "NodeConstraint",
               "datatype": "http://a.example/dt1"
            }
         }
      }
   }
}
Valid: True
No clowns
```

## Constructing a shape from scratch
```python
import ShExJ

schema = ShExJ.Schema()
shape = ShExJ.Shape()
shape.expression = ShExJ.TripleConstraint(predicate="http://a.example/p1",
                                          semActs = [ShExJ.SemAct(name="http://shex.io/extensions/Test", code=" print(o) ")])
schema.shapes = {"http://a.example/S1": shape}
schema._is_valid()
print(schema._as_json_dumps())
```
```text
{
   "type": "Schema",
   "shapes": {
      "http://a.example/S1": {
         "type": "Shape",
         "expression": {
            "type": "TripleConstraint",
            "predicate": "http://a.example/p1",
            "semActs": [
               {
                  "type": "SemAct",
                  "name": "http://shex.io/extensions/Test",
                  "code": " print(o) "
               }
            ]
         }
      }
   }
}
```