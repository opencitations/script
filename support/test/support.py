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
import rdflib
from script.support.support import dict_list_get_by_value_ascii, create_literal, \
    get_resource_number, get_ip, get_ip_id, find_paths
from script.spacin.conf import base_dir, base_iri, default_dir, dir_split_number, items_per_file
from os import sep


class SupportTest(unittest.TestCase):
    @unittest.skip("skip for testing other")
    def test_dict_list_get_by_value_ascii(self):
        expected_output = [
            {"a": "Albért", "c": "Nobody"},
            {"a": "Albert", "b": "Francesco", "c": "Rossi"}
        ]

        input_list = [
            {"a": "John", "b": "Doe"},
            {"a": "Albért", "c": "Nobody"},
            {"a": "Albert", "b": "Francesco", "c": "Rossi"}
        ]
        input_key, input_value = "a", "Albert"

        self.assertEqual(dict_list_get_by_value_ascii(input_list, input_key, input_value), expected_output)

    @unittest.skip("skip for testing other")
    def test_create_literal(self):
        input_g = rdflib.Graph()
        input_res = rdflib.URIRef("http://www.test.net/resource")
        input_p = rdflib.URIRef("http://www.test.net/hasName")
        input_s = "John Doe C¥èal"
        input_datatype = rdflib.XSD["string"]

        self.assertTrue(create_literal(input_g, input_res, input_p, input_s))
        self.assertTrue(create_literal(input_g, input_res, input_p, input_s, input_datatype))

    @unittest.skip("skip for testing other")
    def test_get_resource_number(self):
        expected_output = 123456789123456789123456789

        input_string = "https://w3id.org/oc/corpus/br/123456789123456789123456789"
        self.assertEqual(get_resource_number(input_string), expected_output)
        self.assertEqual(get_resource_number(input_string + "/prov/se/1"), expected_output)

    def test_get_ip(self):
        self.assertEqual(get_ip("lo0"), "127.0.0.1")

    def test_get_ip_id(self):
        self.assertEqual(get_ip_id("lo0"), "1")

    @staticmethod
    def __get_dir(n):
        cur_n = int(n) / dir_split_number
        if int(cur_n) < cur_n:
            cur_n = int(cur_n + 1)
        return str(int(cur_n * dir_split_number))

    @staticmethod
    def __get_file(n):
        cur_n = int(n) / items_per_file
        if int(cur_n) < cur_n:
            cur_n = int(cur_n + 1)

        return SupportTest.__get_dir(n) + "/" + str(int(cur_n * items_per_file))

    def test_find_paths(self):
        base_num = "15"
        base_entity = base_iri + "br/" + base_num
        base_prov = base_entity + "/prov/se/1"
        base_entity_prefix = base_iri + "br/012340" + base_num
        base_prov_prefix = base_iri + "br/012340" + base_num + "/prov/se/1"

        res = find_paths(base_entity, base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_entity, res)
        self.assertEqual(
            res,
            (base_dir + "br" + sep + default_dir + sep + self.__get_dir(base_num),
             base_dir + "br" + sep + default_dir + sep + self.__get_file(base_num) + ".json"))

        res = find_paths(base_prov, base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_prov, res)
        self.assertEqual(
            res,
            (base_dir + "br" + sep + default_dir + sep + self.__get_file(base_num) + sep +
             "prov",
             base_dir + "br" + sep + default_dir + sep + self.__get_file(base_num) + sep +
             "prov" + sep + "se.json"))

        res = find_paths(base_entity_prefix, base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_entity_prefix, res)
        self.assertEqual(
            res,
            (base_dir + "br" + sep + "012340" + sep + self.__get_dir(base_num),
             base_dir + "br" + sep + "012340" + sep + self.__get_file(base_num) + ".json"))

        res = find_paths(base_prov_prefix, base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_prov_prefix, res)
        self.assertEqual(
            res,
            (base_dir + "br" + sep + "012340" + sep + self.__get_file(base_num) + sep +
             "prov",
             base_dir + "br" + sep + "012340" + sep + self.__get_file(base_num) + sep +
             "prov" + sep + "se.json"))

        res = find_paths(base_iri + "prov/pa/1", base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_iri + "prov/pa/1", res)
        self.assertEqual(
            res,
            (base_dir + "prov" + sep + "pa",
             base_dir + "prov" + sep + "pa" + sep + "1.json"))

        res = find_paths(base_iri, base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_iri, res)
        self.assertEqual(
            res,
            (base_dir[:-1],
             base_dir + "index.json"))

        res = find_paths(base_iri + "br/", base_dir, base_iri, default_dir, dir_split_number, items_per_file)
        print(base_iri + "br/", res)
        self.assertEqual(
            res,
            (base_dir + "br",
             base_dir + "br" + sep + "index.json"))


if __name__ == '__main__':
    unittest.main()
