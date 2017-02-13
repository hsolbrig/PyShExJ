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
s = loads(shexj, ShExJ)
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


schema = ShExJ.Schema()
shape = ShExJ.Shape()
shape.expression = ShExJ.TripleConstraint(predicate="http://a.example/p1",
                                          semActs = [ShExJ.SemAct(name="http://shex.io/extensions/Test", code=" print(o) ")])
schema.shapes = {"http://a.example/S1": shape}
schema._is_valid()
print(schema._as_json_dumps())

