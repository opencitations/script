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

# Configuration for local test
base_dir = "./test/data/corpus/"
base_iri = "https://w3id.org/oc/corpus/"
triplestore_url = "http://localhost:3000/blazegraph/sparql"
triplestore_url_real = "https://w3id.org/oc/sparql"
context_path = "https://w3id.org/oc/corpus/context.json"
context_file_path = "./corpus/context.json"
info_dir = "./test/share/id-counter/"
temp_dir_for_rdf_loading = "./test/"
orcid_conf_path = "./script/spacin/orcid_conf.json"
reference_dir = "./test/share/ref/todo/"
reference_dir_error = "./test/index/ref/err/"
reference_dir_done = "./test/index/ref/done/"
dataset_home = "http://opencitations.net/"
dir_split_number = 6  # This must be multiple of the following one
items_per_file = 3
default_dir = "_"
supplier_dir = {
    "1": "01110"
}
interface = "lo0"
do_parallel = False
sharing_dir = "./test/share/data/"
