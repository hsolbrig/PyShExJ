import ShExJ, logger
from jsg import loads
import sys

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
s: ShExJ.Schema = loads(shexj)
print("type(Shema): {}".format(s.type))
S1 = ShExJ.IRI("http://a.example/S1")
print("PREDICATE: {}".format(s.shapes[S1].expression.predicate))
s.shapes[S1].closed = ShExJ.BOOL("true")
print(s._as_json_dumps())
print("Valid: {}".format(s._is_valid()))
s.shapes[S1].clown = ShExJ.INTEGER("17")
print("Valid: {}".format(s._is_valid(logger.Logger(sys.stdout))))
