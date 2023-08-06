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
import jsonasobj
from typing import List, Union

from dbgap.constants import *
from dbgap.file_downloader import FileDownloader


class StudyIdentifier:
    def __init__(self, id_: int, v: int, p: int) -> None:
        """
        GA study identifier, identifier + version and identifier + version + p value
        :param id_: integer study id
        :param v: version number
        :param p: p number
        :return: study id, versioned study id, full identifier

        """
        self.studyid = 'phs%06d' % id_
        self.versionedid = '%s.v%d' % (self.studyid, v)
        self.fullid = '%s.p%d' % (self.versionedid, p)

    @property
    def identifiers(self) -> dict:
        return self.__dict__


def get_study_information(studyid: StudyIdentifier) -> str:
    return FileDownloader(DBGAP_FTP_SERVER).download_file(STUDY_FILE_TEMPLATE % studyid.identifiers)

def list_or_element(arg: Union[List[object], object]) -> object:
    return arg[0] if isinstance(arg, List) else arg


def biocaddie_json(studyid: StudyIdentifier, raw_json: jsonasobj.JsonObj, pht_entries: List[str]) -> jsonasobj.JsonObj:
    """ Convert the raw json image of the dbgap study into a biocaddie equivalent
    :param studyid: Study identifier
    :param raw_json: raw json image
    :param pht_entries:
    :return:
    """
    study = list_or_element(raw_json.GaPExchange.Studies.Study).Configuration
    study_entry = jsonasobj.JsonObj()

    study_entry['@type'] = BIOCADDIE + 'Study'
    study_entry['@id'] = DBGAP + studyid.versionedid
    study_entry.identifierInfo = [dict(identifier=DBGAP + studyid.versionedid, identifierScheme="dbGaP")]
    study_entry.title = study.StudyNameEntrez
    study_entry.description = study.StudyNameReportPage
    study_entry.studyType = list_or_element(study.StudyTypes.StudyType)
    d0 = list_or_element(list_or_element(study.Diseases.Disease))
    study_entry.keywords = d0.vocab_source + ' - ' + d0.vocab_term
    if isinstance(study.Diseases.Disease, List):
        study_entry.keywords += ', ' + ','.join([((e.vocab_source + ' - ') if e.vocab_source != d0.vocab_source else '')
                                                + e.vocab_term for e in study.Diseases.Disease])

    # study_entry.startDate = None
    # study_entry.endDate = None
    # study_entry.duration = None
    # study_entry.location = None
    # study_entry.performedBy = None
    # study_entry.isAboutBiologicalProcess =self.raw
    study_entry.resultsIn = [DBGAP + pht for pht in pht_entries]
    return study_entry
