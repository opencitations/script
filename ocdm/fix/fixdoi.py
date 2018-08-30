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

# This script removes all the duplicated DOIs according to a given list, and leaves those ones that are valid.
# Be aware: this script do not modify the SPARQL endpoint, only the local files

from argparse import ArgumentParser
from json import load
from re import sub, match
from rdflib import URIRef, Graph
from urllib.parse import quote
from requests import get
from requests.exceptions import Timeout
from script.ocdm.graphlib import GraphSet, GraphEntity, ProvSet
from script.ocdm.storer import Storer
from script.spacin.conf import base_iri, context_path, base_dir, temp_dir_for_rdf_loading, context_file_path, \
    dir_split_number, items_per_file, triplestore_url_real, dataset_home, default_dir, info_dir
from script.support.support import find_paths
from script.spacin.resfinder import ResourceFinder
from script.ocdm.datasethandler import DatasetHandler
from os import sep, path, makedirs
from time import sleep


base_api_url = "https://doi.org/api/handles/"
agent_name="FixDOI Script"


def update_all(g_set, remove_entity, full_info_dir):
    prov = ProvSet(g_set, base_iri, context_path, default_dir, full_info_dir,
                   ResourceFinder(base_dir=base_dir, base_iri=base_iri,
                                  tmp_dir=temp_dir_for_rdf_loading,
                                  context_map={context_path: context_file_path},
                                  dir_split=dir_split_number,
                                  n_file_item=items_per_file,
                                  default_dir=default_dir),
                   dir_split_number, items_per_file, "")
    prov.generate_provenance(do_insert=False, remove_entity=remove_entity)

    res_storer = Storer(g_set,
                        context_map={context_path: context_file_path},
                        dir_split=dir_split_number,
                        n_file_item=items_per_file,
                        default_dir=default_dir)

    prov_storer = Storer(prov,
                         context_map={context_path: context_file_path},
                         dir_split=dir_split_number,
                         n_file_item=items_per_file,
                         default_dir=default_dir)

    res_storer.store_all(
        base_dir, base_iri, context_path,
        temp_dir_for_rdf_loading, remove_data=True)

    prov_storer.store_all(
        base_dir, base_iri, context_path,
        temp_dir_for_rdf_loading)

    dset_handler = DatasetHandler(triplestore_url_real,
                                  context_path,
                                  context_file_path, base_iri,
                                  base_dir, "", dataset_home,
                                  temp_dir_for_rdf_loading)
    dset_handler.update_dataset_info(g_set)


if __name__ == "__main__":
    arg_parser = ArgumentParser(agent_name)
    arg_parser.add_argument("-i", "--input", dest="input", required=True,
                            help="The JSON file containing all the brs that have more than one DOI specified. The "
                                 "shape of this file must be a big dictionary having as key the string identifying "
                                 "the br (of the shape 'gbr:1234') and as value a list of strings identifying the ids "
                                 "that are DOIs ('gid:1234').")
    arg_parser.add_argument("-d", "--doi", dest="doi", default="valid_doi.csv",
                            help="The list of valid DOI already found")

    args = arg_parser.parse_args()

    valid_doi = set()
    if path.exists(args.doi):
        with open(args.doi) as f:
            for line in f.readlines():
                stripped_line = line.strip()
                if stripped_line != "":
                    valid_doi.add(stripped_line)

    doi_dir = path.dirname(args.doi)
    if doi_dir != "" and not path.exists(doi_dir):
        makedirs(doi_dir)

    info_dirs = {}

    # It founds the list of ids (DOI) that must be deleted by contacting doi.org API for asking about the validity
    # of the specified DOIs.
    with open(args.input) as f:
        br_doi = load(f)
        for br in br_doi:
            local_id_str = br.replace("gbr:", "")
            supplier_prefix = match("^0[1-9]+0", local_id_str)
            if supplier_prefix is None:
                full_info_dir = info_dir + default_dir + sep
            else:
                full_info_dir = info_dir + supplier_prefix.group(0) + sep

            if full_info_dir not in info_dirs:
                info_dirs[full_info_dir] = {}

            to_remove = info_dirs[full_info_dir]

            id_list = br_doi[br]
            id_len = len(id_list)

            found = False

            with open(args.doi, 'a') as f_doi:
                for cur_id in id_list:
                    cur_doi = cur_id["t"]

                    if cur_doi in valid_doi:
                        id_list.remove(cur_id)
                        found = True
                        break

                    else:
                        tentative = 0
                        while tentative < 5:
                            tentative += 1
                            try:
                                r = get(base_api_url + quote(cur_doi), timeout=30)

                                if r.status_code == 200:
                                    id_list.remove(cur_id)
                                    found = True
                                    f_doi.write(cur_doi + "\n")
                                    valid_doi.add(cur_doi)
                                    break
                            except Exception:
                                sleep(30)
                                continue

            if found:
                to_remove[URIRef(base_iri + sub("^g(..):(.+)$", "\\1/\\2", br))] = \
                    [URIRef(iden) for iden in
                     [base_iri + sub("^g(..):(.+)$", "\\1/\\2", r_id["r"]) for r_id in id_list]]

    s = Storer(context_map={context_path: context_file_path}, dir_split=dir_split_number,
               n_file_item=items_per_file, default_dir=default_dir)

    br_files = {}
    id_files = {}

    update_br = GraphSet(base_iri, context_path)
    remove_id = GraphSet(base_iri, context_path)

    for full_info_dir in info_dirs:
        print("\n\nSupplier directory '%s'" % full_info_dir)
        to_remove = info_dirs[full_info_dir]

        for br in to_remove:
            print("\nAnalyse %s" % br)
            cur_dir, cur_file = find_paths(str(br), base_dir, base_iri, default_dir, dir_split_number, items_per_file)
            if cur_file not in br_files:
                g = s.load(cur_file, tmp_dir=temp_dir_for_rdf_loading)
                br_files[cur_file] = g

            cur_g = br_files[cur_file]
            has_identifier_statements = []

            # For each identifier to remove in a certain br...
            for iden in to_remove[br]:
                print("Analyse %s" % iden)
                t = (br, GraphEntity.has_identifier, iden)
                if t in cur_g:
                    # ... it specify the statement 'br has_identifier id' to be removed in br (after this for block)...
                    has_identifier_statements.append(t)
                    cur_id_dir, cur_id_file = \
                        find_paths(str(iden), base_dir, base_iri, default_dir, dir_split_number, items_per_file)

                    if cur_id_file not in id_files:
                        g_id = s.load(cur_id_file, tmp_dir=temp_dir_for_rdf_loading)
                        id_files[cur_id_file] = g_id

                    cur_id_g = id_files[cur_id_file]

                    # ... and it removes all the statements having id as subject
                    id_entity = remove_id.add_id(agent_name, res=iden)
                    id_entity.add_triples(cur_id_g.triples((iden, None, None)))

            br_entity = update_br.add_br(agent_name, res=br)
            br_entity.add_triples(has_identifier_statements)
            # TODO: eliminare triple dai grafi!!!

        print("Update brs")
        update_all(update_br, False, full_info_dir)
        print("Update ids")
        update_all(remove_id, True, full_info_dir)

print("END")