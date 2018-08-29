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
from script.bee.conf import page_size, supplier_tuple
from script.bee.epmcproc import EuropeanPubMedCentralProcessor
from script.support.stopper import Stopper
from script.support.support import normalise_id
import os
import shutil
import glob
import json


class EuropeanPubMedCentralProcessorTest(unittest.TestCase):

    def setUp(self):
        self.base_dir = "test" + os.sep
        self.csv_file = self.base_dir + "test-stored-ids.csv"
        self.data_dir = self.base_dir + supplier_tuple[0] + os.sep
        self.epmc = EuropeanPubMedCentralProcessor(self.csv_file, "test", "test", "test", Stopper("test"),
                                                   p_size=page_size, debug=False, supplier_idx=supplier_tuple)

    @unittest.skip("It has been used only to create that reference, but the problem is not here.")
    def test_process_references(self):
        self.assertIsNone(self.epmc.process_references("MED", "26246806"))
        self.assertEqual(
            self.epmc.process_references("MED", "15748298"),
            "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/15748298/references/1/1000/json")

    @unittest.skip("It has been used only to create that reference, but the problem is not here.")
    def test_process_xml_source(self):
        self.assertIsNone(self.epmc.process_xml_source("PMC4515293"))
        self.assertEqual(
            self.epmc.process_xml_source("PMC555938"),
            "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC555938/fullTextXML")

    @unittest.skip("It has been used only to create that reference, but the problem is not here.")
    def test_process_article(self):
        self.epmc.process_article("26246806", "MED", "10.1155/2015/634234", "26246806", "PMC4515293", True)
        self.assertIsNone(self.epmc.rs.last_ref_list)

        cur_doi = "10.1186/1471-2105-6-44"
        self.epmc.process_article("15748298", "MED", cur_doi, "15748298", "PMC555938", True)
        result = None
        for cur_file in glob.iglob("%s**%s*%s.json" % (self.data_dir, os.sep, normalise_id(cur_doi)), recursive=True):
            with open(cur_file) as f:
                result = json.load(f)
        self.assertEqual(result["pmcid"], "PMC555938")
        self.assertGreater(len(result["references"]), 0)

    def test_process_article_with_bad_reference(self):
        self.epmc.process_article("27877181", "MED", "10.3389/fpls.2016.01647", "27877181", "PMC5099148", True)

    def tearDown(self):
        os.remove(self.csv_file)
        if os.path.exists(self.data_dir):
            pass  # shutil.rmtree(self.data_dir)


if __name__ == '__main__':
    unittest.main()
