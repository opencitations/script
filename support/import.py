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
from argparse import ArgumentParser
from rdflib import ConjunctiveGraph, URIRef, Literal
from rdflib.namespace import Namespace
from csv import reader
from os import path
from script.spacin.resfinder import ResourceFinder
from script.spacin.conf import base_iri, context_path, base_dir, temp_dir_for_rdf_loading, context_file_path, \
    dir_split_number, items_per_file, triplestore_url_real, dataset_home, default_dir, info_dir, triplestore_url
from script.ocdm.graphlib import GraphSet, ProvSet
from os import sep
from script.ocdm.storer import Storer
from script.ocdm.datasethandler import DatasetHandler

DATACITE = Namespace("http://purl.org/spar/datacite/")
LITERAL = Namespace("http://www.essepuntato.it/2010/06/literalreification/")

# Load the JSON file into a graph
# Find all the subjects
# Convert all DOIs as lowercase
# Find all the brs that are already specified (via DOI or ISBN) and keep track of this table, and substitute them
# Create the GraphSet of all the entity to add
# Create the ProvSet of all the entity to add
# Store everything and update the dataset


agent_name="Import Script"


def check_isbn(id_string, rf):
    res = rf.retrieve_from_isbn(id_string)
    if res is None:
        if len(id_string.replace("-", "").replace("–", "")).strip() == 13:
            if id_string.startswith("978-"):
                res = rf.retrieve_from_isbn(id_string[4:])
            if res is None and id_string.startswith("978"):
                res = rf.retrieve_from_isbn(id_string[3:])
    return res


if __name__ == "__main__":
    arg_parser = ArgumentParser("import.py")
    arg_parser.add_argument("-i", "--input", dest="input", required=True,
                            help="The JSON file containing all data to import.")
    arg_parser.add_argument("-t", "--table", dest="table", required=True,
                            help="The table containing how some items have been included in the OCC.")
    arg_parser.add_argument("-f", "--format", dest="format", default="json-ld",
                            help="The format of the input file to specify.")
    arg_parser.add_argument("-a", "--avoid_sparql_mapping", dest="avoid", default=False, action="store_true",
                            help="This will avoid to query the OCC triplestore for looking for more mappings.")
    arg_parser.add_argument("-sa", "--source_agent", dest="source_agent", default=None,
                            help="The source agent that provided the data to import.")
    arg_parser.add_argument("-s", "--source", dest="source", default=None,
                            help="The URL from which the data have been taken.")
    arg_parser.add_argument("-p", "--prefix", dest="prefix", required=True,
                            help="The prefix used for the resources of the imported file.")
    arg_parser.add_argument("-d", "--done", dest="done", default="done.csv",
                            help="The file which contains the entity that has been already uploaded to the OCC.")

    args = arg_parser.parse_args()

    print("Loading the mapping table")
    mapping_table = {}
    if path.exists(args.table):
        with open(args.table) as f:
            for occ, new in list(reader(f)):
                mapping_table[new] = occ

    print("Loading the file listing the entity that have been already uploaded to the OCC")
    done = set()
    if path.exists(args.done):
        with open(args.done) as f:
            for line in f.readlines():
                stripped_line = line.strip()
                if stripped_line != "":
                    done.add(stripped_line)

    print("Loading the graph")
    g = ConjunctiveGraph()
    g.parse(args.input, format=args.format)

    print("Convert DOIs in lowercase form")
    doi_to_remove = []
    doi_to_add = []
    for s, p, o in g.triples((None, LITERAL.hasLiteralValue, None)):
        o_str = str(o)
        lower_o_str = o_str.lower()
        if o_str != lower_o_str:
            doi_to_remove.append((s, p, o))
            doi_to_add.append((s, p, Literal(lower_o_str)))
    for s, p, o in doi_to_remove:
        g.remove((s, p, o))
    for s, p, o in doi_to_add:
        g.add((s, p, o))

    if not args.avoid:
        print("Check additional mapping in the OCC triplestore")
        rf = ResourceFinder(ts_url=triplestore_url, default_dir=default_dir)
        with open(args.table, "a") as f:
            for s, p, o in g.triples((None, DATACITE.hasIdentifier, None)):
                if str(s) not in mapping_table:
                    is_doi = False
                    is_isbn = False
                    id_string = None
                    for s1, p2, o2 in g.triples((o, None, None)):
                        if p2 == DATACITE.usesIdentifierScheme:
                            if o2 == DATACITE.doi:
                                is_doi = True
                            elif o2 == DATACITE.isbn:
                                is_isbn = True
                        elif p2 == LITERAL.hasLiteralValue:
                            id_string = str(o2).strip()

                    res = None
                    if is_doi:
                        res = rf.retrieve_from_doi(id_string)
                    elif is_isbn:
                        res = check_isbn(id_string, rf)
                        if res is None:
                            res = check_isbn(id_string.replace("-", "").replace("–", ""), rf)

                    if res is not None:
                        mapping_table[str(s)] = str(res)
                        f.write("%s,%s\n" % (str(s), str(res)))

    print("Change resources that already exist in the OCC.")
    for item in mapping_table:
        for s, p, o in g.triples((None, None, URIRef(item))):
            g.add((s, p, URIRef(mapping_table[item])))
            g.remove((s, p, o))

        resource_to_remove = set()
        resource_to_remove.add(URIRef(item))

        while len(resource_to_remove):
            res = resource_to_remove.pop()
            for s, p, o in g.triples((res, None, None)):
                g.remove((s, p, o))
                if type(o) is URIRef and "/br/" not in str(o):
                    resource_to_remove.add(o)



    full_info_dir = info_dir + args.prefix + sep

    print("Generate data compliant with the OCDM.")
    gs = GraphSet(base_iri, context_path)
    for s in g.subjects():
        with open(args.done, "a") as f:
            s_string = str(s)
            if s_string not in done:
                entity = None
                if "/ar/" in s_string:
                    entity = gs.add_ar(agent_name, source_agent=args.source_agent, source=args.source, res=s)
                elif "/be/" in s_string:
                    entity = gs.add_be(agent_name, source_agent=args.source_agent, source=args.source, res=s)
                elif "/br/" in s_string:
                    entity = gs.add_br(agent_name, source_agent=args.source_agent, source=args.source, res=s)
                elif "/id/" in s_string:
                    entity = gs.add_id(agent_name, source_agent=args.source_agent, source=args.source, res=s)
                elif "/ra/" in s_string:
                    entity = gs.add_ra(agent_name, source_agent=args.source_agent, source=args.source, res=s)
                elif "/re/" in s_string:
                    entity = gs.add_re(agent_name, source_agent=args.source_agent, source=args.source, res=s)

                if entity is not None:
                    entity.add_triples(g.triples((s, None, None)))
                    done.add(s_string)
                    f.write(s_string + "\n")
                else:
                    print("Something went wrong with resource '%s'." % s_string)

    prov = ProvSet(gs, base_iri, context_path, default_dir, full_info_dir,
                   ResourceFinder(base_dir=base_dir, base_iri=base_iri,
                                  tmp_dir=temp_dir_for_rdf_loading,
                                  context_map={context_path: context_file_path},
                                  dir_split=dir_split_number,
                                  n_file_item=items_per_file,
                                  default_dir=default_dir),
                   dir_split_number, items_per_file, "")   # Prefix set to "" so as to avoid it for prov data
    prov.generate_provenance()

    print("Store the data.")
    res_storer = Storer(gs,
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
        temp_dir_for_rdf_loading)

    prov_storer.store_all(
        base_dir, base_iri, context_path,
        temp_dir_for_rdf_loading)

    print("Update the dataset description.")
    dset_handler = DatasetHandler(triplestore_url_real,
                                  context_path,
                                  context_file_path, base_iri,
                                  base_dir, full_info_dir, dataset_home,
                                  temp_dir_for_rdf_loading)
    dset_handler.update_dataset_info(gs)
