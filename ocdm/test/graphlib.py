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
from script.ocdm.graphlib import GraphEntity, GraphSet
from rdflib import Graph, URIRef
from script.spacin.conf import base_iri, context_path, info_dir, items_per_file


class GraphlibTest(unittest.TestCase):
    def setUp(self):
        self.fe = URIRef("fake_res")

    def __new_ge(self):
        return GraphEntity(Graph(), self.fe, g_set=GraphSet(base_iri, context_path, info_dir, items_per_file, ""))

    def test_create_pub_date(self):
        ge = self.__new_ge()
        ge.create_pub_date([2018, 1, 1])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018")

        ge = self.__new_ge()
        ge.create_pub_date([2018, 1])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018-01")

        ge = self.__new_ge()
        ge.create_pub_date([2018, 1, 15])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018-01-15")

        ge = self.__new_ge()
        ge.create_pub_date([2018, 12, 1])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018-12-01")

        ge = self.__new_ge()
        ge.create_pub_date([2018, 3, 1])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018-03-01")

        ge = self.__new_ge()
        ge.create_pub_date([2018, 3, 23])
        self.assertEqual(str(next(ge.g.objects(self.fe, GraphEntity.has_publication_date))), "2018-03-23")


if __name__ == '__main__':
    unittest.main()
