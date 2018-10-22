#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Silvio Peroni <essepuntato@gmail.com>
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

from datetime import datetime
from os.path import abspath, isdir, sep
from os import walk
from argparse import ArgumentParser

from SPARQLWrapper import SPARQLWrapper


def add(server, g_url, f_n, date_str):
    server = SPARQLWrapper(server)
    server.method = 'POST'
    server.setQuery('LOAD <file:' + abspath(f_n) + '> INTO GRAPH <' + g_url + '>')
    server.query()

    with open("updatetp_report_%s.txt" % date_str, "a") as h:
        h.write("Added file '%s'\n" % f_n)


if __name__ == "__main__":
    arg_parser = ArgumentParser("updatetp.py", description="Update a triplestore with a given "
                                                           "input .nt file of new triples and "
                                                           "the graph enclosing them.")
    arg_parser.add_argument("-s", "--sparql_endpoint",
                            dest="se_url", required=True,
                            help="The URL of the SPARQL endpoint.",
                            default="http://localhost:3000/blazegraph/sparql")
    arg_parser.add_argument("-i", "--input_file", dest="input_file", required=True,
                            help="The path to the NT file to upload on the triplestore.")
    arg_parser.add_argument("-g", "--graph", dest="graph_name", required=True,
                            help="The graph URL to associate to the triples.")

    args = arg_parser.parse_args()

    SE_URL = args.se_url
    INPUT_FILE = args.input_file
    GRAPH_URL = args.graph_name
    date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    print("# Process starts")

    all_files = []
    if isdir(INPUT_FILE):
        for cur_dir, cur_subdir, cur_files in walk(INPUT_FILE):
            for cur_file in cur_files:
                if cur_file.endswith(".nt"):
                    all_files.append(cur_dir + sep + cur_file)
    else:
        all_files.append(INPUT_FILE)

    for cur_file in all_files:
        print("\nUploading file '%s'" % cur_file)
        add(SE_URL, GRAPH_URL, cur_file, date_str)
        print("Done.")

    print("# Process ends")