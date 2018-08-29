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

import unittest
from script.ocdm.storer import Storer
from rdflib import Graph, URIRef
from rdflib.namespace import FOAF
from script.spacin.conf import base_iri, context_path, items_per_file, dir_split_number, base_dir, temp_dir_for_rdf_loading, context_file_path, default_dir


class StorerTest(unittest.TestCase):
    def setUp(self):
        cur_g = Graph(identifier=base_iri + "br/")
        cur_g.add((URIRef(base_iri + "br/022201"), FOAF.maker, URIRef(base_iri + "ra/011101")))
        self.g = cur_g

        self.s = Storer(None,
                        context_map={context_path: context_file_path},
                        dir_split=dir_split_number,
                        n_file_item=items_per_file,
                        default_dir=default_dir)

    def test_store(self):
        result = self.s.store(self.g, base_dir, base_iri, context_path, temp_dir_for_rdf_loading, store_now=False)
        print(list(result.keys())[0], list(result.values())[0].serialize(format="nquads"))

    # TODO: test update


if __name__ == '__main__':
    unittest.main()
