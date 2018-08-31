#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

__author__ = 'essepuntato'

import argparse
import os
from re import match, sub
from script.support.reporter import Reporter
from script.ocdm.storer import Storer
from script.spacin.conf import context_path, context_file_path, dir_split_number, items_per_file, \
    default_dir, temp_dir_for_rdf_loading


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("creatent.py",
                                         description="This script create an nt file given a directory "
                                                     "of the OCC containing data")
    arg_parser.add_argument("-i", "--input", dest="input", required=True,
                            help="The directory containing the json-ld data.")
    arg_parser.add_argument("-o", "--output", dest="output", required=True,
                            help="The output file.")

    args = arg_parser.parse_args()

    repok = Reporter(True, prefix="[creatent.py: INFO] ")
    reperr = Reporter(True, prefix="[creatent.py: ERROR] ")
    repok.new_article()
    reperr.new_article()

    s = Storer(context_map={context_path: context_file_path}, dir_split=dir_split_number,
               n_file_item=items_per_file, default_dir=default_dir)

    for cur_dir, cur_subdir, cur_files in os.walk(args.input):
        with open(args.output, 'a') as f:
            for cur_file in cur_files:
                if match("^[0-9]+\.json", cur_file) is not None:
                    cur_g = s.load(cur_dir + os.sep + cur_file, tmp_dir=temp_dir_for_rdf_loading)
                    nt_strings = cur_g.serialize(format="nt11", encoding="utf-8").decode("utf-8")
                    f.write(nt_strings)

    repok.add_sentence("Done.")
    if not reperr.is_empty():
        reperr.write_file("creatent.rep.%s.err.txt" % (
            sub("_+", "_", sub("[\.%s/]" % os.sep, "_", args.input))))
