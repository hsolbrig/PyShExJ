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

import unittest
from typing import Optional, Union, List, Dict, Set
from typing_patch import conforms, as_type


class ConformsTestCase(unittest.TestCase):
    def test_union(self):
        self.assertTrue(conforms(None, Optional[int]))
        self.assertFalse(conforms(None, Union[int, str]))
        self.assertTrue(conforms(None, Union[int, str, None]))
        self.assertTrue(conforms("abc", Union[int, str, None]))
        self.assertTrue(conforms(1, Union[int, str]))
        self.assertFalse(conforms([1], Union[int, str]))
        self.assertTrue(conforms(["abc"], Union[int, str, List[str]]))
        self.assertFalse(conforms([1], Union[int, str, List[str]]))

    def test_dict(self):
        self.assertTrue(conforms({}, Dict[str, Union[bool, int, str]]))
        self.assertTrue(conforms({"a": True}, Dict[str, Union[bool, int, str]]))
        self.assertTrue(conforms({"a": True, "b": 1, "c": "def"}, Dict[str, Union[bool, int, str]]))

    def test_list(self):
        self.assertTrue(conforms([], List[str]))
        self.assertTrue(conforms(["abc", "def"], List[str]))
        self.assertFalse(conforms(["abc", 1], List[str]))
        self.assertTrue(conforms([["abc"], ["def"]], List[List[str]]))
        self.assertFalse(conforms([[1]], List[List[str]]))

    def test_set(self):
        self.assertTrue(conforms([], Set[str]))


class AsTypeTestCase(unittest.TestCase):
    def test_basics(self):
        self.assertEqual("abc", as_type("abc", str))
        self.assertEqual("abc", as_type("abc", Union[str, int]))


if __name__ == '__main__':
    unittest.main()
