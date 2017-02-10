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
from typing import List
import dirlistproc
from argparse import Namespace
from jsg import load
import ShExJ                    # Needed to get the definitions loaded
from logger import Logger


def proc_shexj(input_fn: str, _output_fn: str, _opts: Namespace) -> bool:
    """
    entry point point for dirlistproc process
    :param input_fn: ShExJ file to validate
    :param _output_fn: output file name (unused)
    :param opts: input options (unused)
    :return: success/failure indicator
    """
    s = load(open(input_fn))
    if not s._is_valid(log = Logger(sys.stdout)):
        print("***** ERROR: {}".format(input_fn))
        return False
    return True


def file_filter(fn: str, dir: str, opts:Namespace) -> bool:
    return "futureWork" not in dir and not fn.startswith("coverage")


def main(argv: List[str]):
    """
    Process a set of FHIR ttl instances, validating them against the ShEx service.
    """
    dlp = dirlistproc.DirectoryListProcessor(argv, "Validate ShExJ", ".json", None)
    nfiles, nsuccess = dlp.run(proc_shexj, file_filter_2=file_filter)
    print("Total=%d Successful=%d" % (nfiles, nsuccess))


if __name__ == '__main__':
    main(sys.argv[1:])
