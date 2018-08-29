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

import json
import traceback
from datetime import datetime
import re
import shutil
from script.spacin.conf import reference_dir, base_iri, context_path, info_dir, triplestore_url, orcid_conf_path, \
    base_dir, temp_dir_for_rdf_loading, context_file_path, dir_split_number, items_per_file, triplestore_url_real, \
    dataset_home, reference_dir_done, reference_dir_error, interface, supplier_dir, default_dir, do_parallel, \
    sharing_dir
from script.support.stopper import Stopper
from script.spacin.crossrefproc import CrossrefProcessor
from script.spacin.resfinder import ResourceFinder
from script.spacin.orcidfinder import ORCIDFinder
from script.ocdm.graphlib import ProvSet
from script.ocdm.storer import Storer
from script.ocdm.datasethandler import DatasetHandler
from script.support.support import move_file, get_ip_id
from os import sep, walk, path, listdir, makedirs

start_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
error = False
last_file = None
s = Stopper(reference_dir)
try:
    local_id = get_ip_id(interface)
    supplier_prefix = ""
    if local_id in supplier_dir:
        supplier_prefix = supplier_dir[local_id]
        real_dir = supplier_prefix + sep
    else:
        real_dir = default_dir + sep

    full_reference_dir = reference_dir + real_dir
    full_info_dir = info_dir + real_dir

    for cur_dir, cur_subdir, cur_files in walk(full_reference_dir):
        if s.can_proceed():
            for cur_file in sorted(cur_files):
                if s.can_proceed():
                    if cur_file.endswith(".json"):
                        cur_file_path = cur_dir + sep + cur_file
                        cur_local_dir_path = re.sub("^([0-9]+-[0-9]+-[0-9]+-[0-9]+).+$", "\\1", cur_file)
                        with open(cur_file_path) as fp:
                            last_file = cur_file_path
                            last_local_dir = cur_local_dir_path
                            print("\n\nProcess file '%s'\n" % cur_file_path)
                            json_object = json.load(fp)
                            crp = CrossrefProcessor(base_iri, context_path, full_info_dir, json_object,
                                                    ResourceFinder(ts_url=triplestore_url, default_dir=default_dir),
                                                    ORCIDFinder(orcid_conf_path), items_per_file, supplier_prefix)
                            result = crp.process()
                            if result is not None:
                                prov = ProvSet(result, base_iri, context_path, default_dir, full_info_dir,
                                               ResourceFinder(base_dir=base_dir, base_iri=base_iri,
                                                              tmp_dir=temp_dir_for_rdf_loading,
                                                              context_map=
                                                              {context_path: context_file_path},
                                                              dir_split=dir_split_number,
                                                              n_file_item=items_per_file,
                                                              default_dir=default_dir),
                                               dir_split_number, items_per_file, supplier_prefix)
                                prov.generate_provenance()

                                res_storer = Storer(result,
                                                    context_map={context_path: context_file_path},
                                                    dir_split=dir_split_number,
                                                    n_file_item=items_per_file,
                                                    default_dir=default_dir)

                                prov_storer = Storer(prov,
                                                     context_map={context_path: context_file_path},
                                                     dir_split=dir_split_number,
                                                     n_file_item=items_per_file)

                                if do_parallel:
                                    base_share_dir = sharing_dir + sep + real_dir + \
                                                     datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + sep
                                    if not path.exists(base_share_dir):
                                        makedirs(base_share_dir)

                                    res_storer.store_graphs_in_file(base_share_dir + "data.json", context_path)
                                    prov_storer.store_graphs_in_file(base_share_dir + "prov.json", context_path)
                                else:
                                    res_storer.upload_and_store(
                                        base_dir, triplestore_url, base_iri, context_path,
                                        temp_dir_for_rdf_loading)

                                    prov_storer.store_all(
                                        base_dir, base_iri, context_path,
                                        temp_dir_for_rdf_loading)

                                    dset_handler = DatasetHandler(triplestore_url_real,
                                                                  context_path,
                                                                  context_file_path, base_iri,
                                                                  base_dir, full_info_dir, dataset_home,
                                                                  temp_dir_for_rdf_loading)
                                    dset_handler.update_dataset_info(result)

                                # If everything went fine, move the input file to the done directory
                                move_file(cur_file_path,
                                          reference_dir_done + sep + cur_local_dir_path)

                            # If something in the process went wrong, move the input file
                            # in an appropriate directory
                            else:
                                if crp.reperr.is_empty():  # The resource has been already processed
                                    move_file(cur_file_path,
                                              reference_dir_done + sep + cur_local_dir_path)
                                else:
                                    moved_file = \
                                        move_file(cur_file_path,
                                                  reference_dir_error + sep + cur_local_dir_path)
                                    crp.reperr.write_file(moved_file + ".err")

                            cur_dir_path = path.dirname(cur_file_path)
                            if len([name for name in listdir(cur_dir_path)
                                    if name.endswith(".json")]) == 0:
                                shutil.rmtree(cur_dir_path)
                else:
                    print("\n\nProcess stopped due to external reasons")
                    break
        else:
            print("\n\nProcess stopped due to external reasons")
            break
except Exception as e:
    exception_string = str(e) + " " + traceback.format_exc().rstrip("\n+")
    print(exception_string)
    if last_file is not None:
        moved_file = move_file(last_file, reference_dir_error + sep + last_local_dir)
        with open(moved_file + ".err", "w") as f:
            f.write(exception_string)
        cur_dir_path = path.dirname(last_file)
        if len([name for name in listdir(cur_dir_path)
                if name.endswith(".json")]) == 0:
            shutil.rmtree(cur_dir_path)
end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
print("\nStarted at:\t%s\nEnded at:\t%s" % (start_time, end_time))