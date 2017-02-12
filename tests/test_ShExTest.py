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

import os
import dirlistproc
from argparse import Namespace
from jsg import loads as jsg_loads
from jsonasobj import loads as jao_loads
from dict_compare import compare_dicts
import ShExJ
from logger import Logger
from memlogger import MemLogger


testDir = os.path.join("..", "..", "..", "shexSpec", "shexTest", "schemas")
batch = False


def compare_json(j1, j2, log):
    d1 = jao_loads(j1)._as_dict
    d2 = jao_loads(j2)._as_dict
    return compare_dicts(d1, d2, file=log)


def proc_shexj(input_fn: str, _output_fn: str, _opts: Namespace) -> bool:
    """
    entry point point for dirlistproc process
    :param input_fn: ShExJ file to validate
    :param _output_fn: output file name (unused)
    :param opts: input options (unused)
    :return: success/failure indicator
    """
    log = MemLogger("\t")
    with open(input_fn) as f:
        json_str = f.read()
        s = jsg_loads(json_str)
        if not s._is_valid(log=Logger(log)):
            print("File: {} - ".format(input_fn))
            print(log.log)
            return False
        else:
            if not compare_json(json_str, s._as_json, log):
                print("File: {} - ".format(input_fn))
                print(log.log)
                return False
        return True


def file_filter(fn, dir,  _):
    return (dir is None or "futureWork" not in dir) and (fn is None or not fn.startswith("coverage"))


class ValidationTestCase(unittest.TestCase):

    def testSpecSchema(self):
        dlp = dirlistproc.DirectoryListProcessor(["-id", testDir], "Validate ShExJ", ".json", None)
        nfiles, nsuccess = dlp.run(lambda *argv: proc_shexj(*argv), file_filter_2=file_filter)
        print("Files: {}, Errors: {}".format(nfiles, nfiles-nsuccess))


if __name__ == '__main__':
    unittest.main()

