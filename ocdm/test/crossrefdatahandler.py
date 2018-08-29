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
from requests import get
from json import loads, dumps
from script.ocdm.crossrefdatahandler import CrossrefDataHandler


class CrossrefDataHandlerTest(unittest.TestCase):
    def setUp(self):
        self.cdh = CrossrefDataHandler()
        self.source = "http://api.crossref.org/works/10.1108/JD-12-2013-0166"
        self.json = loads(get(self.source).text)["message"]

    def test_process_json(self):
        br = self.cdh.process_json(self.json, self.source, "Silvio", "Crossref", "http://www.essepuntato.it")
        br.g.serialize("test/test.ttl", format="turtle")


if __name__ == '__main__':
    unittest.main()
