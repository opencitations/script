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
debug = True
base_dir = "./test/index/ref/"
share_dir = "./test/share/ref/"
reference_dir = share_dir + "todo/"
error_dir = base_dir + "issue/"
stored_file = share_dir + "stored-ids.csv"
pagination_file = share_dir + "epmc-pp.txt"
page_size = 2
supplier_tuple = (
    "01110", "01120", "01130", "01140", "01150", "01160", "01170", "01180", "01190", "01910",
    "01210", "01220", "01230", "01240", "01250", "01260", "01270", "01280", "01290", "01920",
    "01310", "01320", "01330", "01340", "01350", "01360", "01370", "01380", "01390", "01930"
)

