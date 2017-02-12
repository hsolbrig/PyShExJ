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
import sys
import unittest
from ShExJ import *
from logger import Logger
from memlogger import MemLogger
from jsg import loads


class FunctionTestCase(unittest.TestCase):
    def testConstructor(self):
        s = Schema()
        self.assertTrue(s._is_valid())
        s = Schema(base=IRI("http://example.org/"))
        self.assertTrue(s._is_valid())
        sh = Shape()
        sh.closed = BOOL("true")
        self.assertTrue(sh._is_valid())
        s.shapes = {IRI("S1"): sh}
        self.assertTrue(s._is_valid())

    def testLoader1(self):
        shexj = """{ "type": "NodeConstraint", "datatype": "http://a.example/dt1" }"""
        s = loads(shexj)
        self.assertTrue(s._is_valid())

    def testLoader2(self):
        shexj = """{
              "type": "Shape",
              "expression": {
                "type": "TripleConstraint",
                "predicate": "http://a.example/p1",
                "valueExpr": { "type": "NodeConstraint", "datatype": "http://a.example/dt1" }
               }
            }"""
        s = loads(shexj)
        self.assertTrue(isinstance(s, Shape) and s._is_valid())

    def testLoader(self):
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
        s = loads(shexj)
        self.assertTrue(s._is_valid())
        self.assertEqual("""{
   "type": "Schema",
   "shapes": {
      "http://a.example/S1": {
         "type": "Shape",
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
}""", s._as_json_dumps())

    def test_closed(self):
        shexj = """{
  "type": "Schema",
  "shapes":{
    "http://a.example/S1": {
      "type": "Shape",
      "closed": true
    }
  }
}"""
        s: Schema = loads(shexj)
        self.assertTrue(s._is_valid())
        self.assertTrue(s.shapes["http://a.example/S1"].closed == True)


if __name__ == '__main__':
    unittest.main()
