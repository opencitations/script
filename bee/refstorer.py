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

import os
import csv
import json
from script.support.support import normalise_id
from datetime import datetime
import argparse
import re


class BibliographicReferenceStorer(object):
    def __init__(self, stored_file, reference_dir, error_dir, supplier_idx=()):
        self.ref_dir = reference_dir
        self.err_dir = error_dir
        self.stored = set()
        self.last_ref_list = None
        self.error = False
        self.csv_file = stored_file
        self.supplier_idx = supplier_idx
        self.supplier_idx_pos = -1
        if os.path.exists(self.csv_file):
            with open(self.csv_file) as f:
                csv_ids = csv.reader(f)
                for row in csv_ids:
                    self.stored.add(row[0])
        else:  # Create the file
            file_dir_path = os.path.dirname(self.csv_file)
            if not os.path.exists(file_dir_path):
                os.makedirs(file_dir_path)
            open(self.csv_file, "a").close()

    def is_any_stored(self, id_list):
        for string_id in id_list:
            if self.is_stored(string_id):
                return True
        return False

    def is_stored(self, string_id):
        if string_id is None:
            return False
        else:
            return string_id in self.stored

    def new_ref_list(self):
        self.last_ref_list = []
        self.error = False

    def new_supplier(self):
        try:
            self.supplier_idx_pos = (self.supplier_idx_pos + 1) % len(self.supplier_idx)
            return self.supplier_idx[self.supplier_idx_pos] + os.sep
        except IndexError:
            return ""

    def add_reference(self, bib_entry=None, process_it=True,
                      string_local_id=None, string_doi=None,
                      string_pmid=None, string_pmcid=None, string_url=None):
        if self.last_ref_list is not None and not self.error:
            cur_reference = {}

            if bib_entry is not None:
                cur_reference["bibentry"] = bib_entry
                cur_reference["process_entry"] = str(process_it)
            if string_local_id is not None:
                cur_reference["localid"] = string_local_id
            if string_doi is not None:
                cur_reference["doi"] = string_doi
            if string_pmid is not None:
                cur_reference["pmid"] = string_pmid
            if string_pmcid is not None:
                cur_reference["pmcid"] = string_pmcid
            if string_url is not None:
                cur_reference["url"] = string_url

            if cur_reference:
                self.last_ref_list += [cur_reference]
            else:
                self.error = True
                self.last_ref_list = []

            return True
        else:
            return False

    def store(self, id_string, citing_localid=None, citing_doi=None, citing_pmid=None, citing_pmcid=None,
              curator=None, source_provider=None, source=None):
        if self.last_ref_list is not None:

            json_item = {}
            if self.last_ref_list:
                json_item["references"] = self.last_ref_list
            if citing_localid is not None:
                json_item["localid"] = citing_localid
            if citing_doi is not None:
                json_item["doi"] = citing_doi
            if citing_pmid is not None:
                json_item["pmid"] = citing_pmid
            if citing_pmcid is not None:
                json_item["pmcid"] = citing_pmcid
            if curator is not None:
                json_item["curator"] = curator
            if source_provider is not None:
                json_item["source_provider"] = source_provider
            if source is not None:
                json_item["source"] = source

            cur_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f_')
            local_file_name = cur_time + normalise_id(id_string) + ".json"
            local_dir_name = self.new_supplier() + re.sub("^([0-9]+-[0-9]+-[0-9]+-[0-9]+).+$", "\\1", cur_time)
            # The error variable is True if a reference in the reference list
            # has no information at all
            if self.error:
                new_dir_path = self.err_dir + os.sep + local_dir_name
                new_file_path = new_dir_path + os.sep + local_file_name
            else:
                new_dir_path = self.ref_dir + os.sep + local_dir_name
                new_file_path = new_dir_path + os.sep + local_file_name
                
            if not os.path.exists(new_dir_path):
                os.makedirs(new_dir_path)
            
            with open(new_file_path, "w") as f:
                json.dump(json_item, f, indent=4, ensure_ascii=False)

            if id_string not in self.stored:
                with open(self.csv_file, "a") as name_f:
                    name_f.write(id_string + "\n")
                    self.stored.add(id_string)

            self.new_ref_list()
            return True

        return False
