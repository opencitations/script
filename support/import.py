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
from argparse import ArgumentParser
from rdflib import ConjunctiveGraph, URIRef
from rdflib.namespace import Namespace

DATACITE = Namespace("http://purl.org/spar/datacite/")
LITERAL = Namespace("http://www.essepuntato.it/2010/06/literalreification/")

# Load the JSON file into a graph
# Find all the subjects
# Convert all DOIs as lowercase
# Find all the brs that are already specified (via DOI or ISBN) and keep track of this table, and substitute them
# Create the GraphSet of all the entity to add
# Create the ProvSet of all the entity to add
# Store everything and update the dataset

if __name__ == "__main__":
    arg_parser = ArgumentParser("import.py")
    arg_parser.add_argument("-i", "--input", dest="input", required=True,
                            help="The JSON file containing all data to import.")
    arg_parser.add_argument("-t", "--table", dest="table", required=True,
                            help="The table containing how some items have been included in the OCC.")
    arg_parser.add_argument("-f", "--format", dest="format", default="json-ld",
                            help="The format of the input file to specify.")

    args = arg_parser.parse_args()
    g = ConjunctiveGraph()
    g.parse(args.input, format=args.format)

    doi_to_remove = []
    doi_to_add = []
    for s, p, o in g.triples((None, LITERAL.hasLiteralValue, None)):
        o_str = str(o)
        lower_o_str = o_str.lower()
        if o_str != lower_o_str:
            pass  # TODO: do things


