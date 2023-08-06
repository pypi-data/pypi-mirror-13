# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
from pyld import jsonld
import jsonasobj
from rdflib import Graph

# TODO: do this right
prefixes = """
@prefix dbgap: <http://www.ncbi.nlm.nih.gov/gap/mms#> .
@prefix biocaddie: <http://biocaddie.org/mms#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix fhir: <http://hl7.org/fhir/mms#> .
@prefix mms: <http://rdf.cdisc.org/mms#> .
@prefix dct: <http://purl.org/dc/terms/> .
"""


def json_to_rdf(json_in: jsonasobj.JsonObj, schema_uri: str) -> Graph:
    """ Use the jsonld processor to convert the json into an RDF graph
    :param json_in:
    :param schema_uri: the base URI of the schema file
    :return: RDF graph
    """
    json_in['@context'] = schema_uri + ('/' if schema_uri[-1] not in ['/', '#'] else '') + 'context.json'
    normalized = jsonld.normalize(json_in._as_json_obj(), {'format': 'application/nquads', 'algorithm': 'URDNA2015'})
    g = Graph()
    g.parse(data=prefixes, format="turtle")
    g.parse(data=normalized, format="turtle")
    return g

