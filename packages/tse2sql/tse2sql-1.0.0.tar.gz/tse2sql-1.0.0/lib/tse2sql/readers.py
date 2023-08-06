# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Carlos Jenkins
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
TSE files parsing / reading module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from logging import getLogger
from datetime import datetime
from traceback import format_exc
from collections import OrderedDict
from codecs import open as open_with_encoding

from inflection import titleize

from .utils import get_file, count_lines


log = getLogger(__name__)


class DistrictsReader(object):
    """
    Read and parse the ``Distelec.txt`` file.

    The ``Distelec.txt`` file is a CSV file in the form:

    ::

        101001,SAN JOSE,CENTRAL,HOSPITAL
        101002,SAN JOSE,CENTRAL,ZAPOTE
        101003,SAN JOSE,CENTRAL,SAN FRANCISCO DE DOS RIOS
        101004,SAN JOSE,CENTRAL,URUCA
        101005,SAN JOSE,CENTRAL,MATA REDONDA
        101006,SAN JOSE,CENTRAL,PAVAS

    - It list the provinces, cantons and districts of Costa Rica.
    - It is encoded in ``ISO-8859-15`` and uses Windows CRLF line terminators.
    - It is quite stable. It will only change when Costa Rica districts change
      (quite uncommon, but happens from time to time).
    - It is relatively small. Costa Rica has 81 cantons, and ~6 or so
      districts per canton. As of 2016, Costa Rica has 478 districts.
      As this writting, the CSV file is 172KB in size.
    - The semantics of the code is as following:

      ::

          <province(1 digit)><canton(2 digits)><district(3 digits)>

      Please note that only the province code is unique. Both canton and
      districts codes are reused and thus depend on the value of the previous
      code.

    This class will lookup for the file and will process it completely in main
    memory in order to build provinces, cantons and districts tables at the
    same time. Also, the file will be processed even if some lines are
    malformed. Any error will be logged as such.
    """

    def __init__(self, search_dir):
        self._search_dir = search_dir
        self._filename = get_file(search_dir, 'Distelec.txt')
        self._bad_data = []
        self.provinces = OrderedDict()
        self.cantons = OrderedDict()
        self.districts = OrderedDict()

    def parse(self):
        """
        Open and parse the ``Distelec.txt`` file.

        After parsing the following attributes will be available:

        :var provinces: Dictionary with province id as key and name as value.
        :var cantons: Dictionary with a tuple ``(province id, canton id)`` as
         key and name as value.
        :var districts: Dictionary with a tuple
         ``(province id, canton id, district id)`` as key and name as value.
        """
        with open_with_encoding(self._filename, 'rb', 'iso8859-15') as fd:
            for linenum, line in enumerate(fd, 1):
                line = line.strip()

                if not line:
                    log.warning(
                        'Distelec.txt :: Ignoring empty line #{}'.format(
                            linenum
                        )
                    )
                    continue

                try:
                    parts = line.split(',')
                    assert len(parts) == 4

                    # Get codes
                    code = int(parts[0])

                    # Insert province
                    province_code = code // 100000
                    province_name = titleize(parts[1].strip())

                    if province_code in self.provinces:
                        assert self.provinces[province_code] == province_name
                    else:
                        self.provinces[province_code] = province_name

                    # Insert canton
                    canton_code = (code % 100000) // 1000
                    canton_key = (province_code, canton_code)
                    canton_name = titleize(parts[2].strip())

                    if canton_code in self.cantons:
                        assert self.cantons[canton_key] == canton_name
                    else:
                        self.cantons[canton_key] = canton_name

                    # Insert district
                    district_code = code % 1000
                    district_key = (province_code, canton_code, district_code)
                    district_name = titleize(parts[3].strip())
                    if district_code in self.districts:
                        assert self.districts[district_key] == district_name
                    else:
                        self.districts[district_key] = district_name

                except Exception:
                    self._bad_data.append(linenum)
                    log.error(
                        'Distelec.txt :: Bad data at line #{}:\n{}'.format(
                            linenum, line
                        )
                    )
                    log.debug(format_exc())
                    continue

    def analyse(self):
        """
        Return a small report with some basic analysis of the tables.

        :return: A dictionary with the analysis of data provided by the parsed
         file. In particular, the amount of provinces, cantons and districts,
         the largest name of those, and the bad lines found.
        :rtype: A dict of the form:

         ::

            analysis = {
                'provinces': ...,
                'provinces_extended': ...,
                'province_largest': ...,
                'cantons': ...,
                'cantons_extended': ...,
                'cantons_largest': ...,
                'districts': ...,
                'districts_extended': ...,
                'districts_largest': ...,
                'bad_data': ...
            }
        """
        def count_exclude_consulates(dictionary):
            return sum(1 for key in dictionary if key[0] != 8)

        analysis = {
            # This will hardly change, anyhow...
            'provinces': len(self.provinces) - 1,
            'provinces_extended': len(self.provinces),
            'province_largest': max(self.provinces.values(), key=len),
            'cantons': count_exclude_consulates(self.cantons),
            'cantons_extended': len(self.cantons),
            'cantons_largest': max(self.cantons.values(), key=len),
            'districts': count_exclude_consulates(self.districts),
            'districts_extended': len(self.districts),
            'districts_largest': max(self.districts.values(), key=len),
            'bad_data': self._bad_data
        }
        return analysis


class VotersReader(object):
    """
    Read and parse the ``PADRON_COMPLETO.txt`` file.

    The ``PADRON_COMPLETO.txt`` file is a CSV file in the form:

    ::

        100339724,109007,1,20231119,01031,JOSE                          ,DELGADO                   ,CORRALES
        100429200,109006,2,20221026,01025,PAULA                         ,QUIROS                    ,QUIROS
        100697455,101023,2,20150620,00073,CARMEN                        ,FALLAS                    ,GUEVARA
        100697622,101020,2,20230219,00050,ANTONIA                       ,RAMIREZ                   ,CARDENAS
        100720641,108002,2,20241119,00884,SOLEDAD                       ,SEQUEIRA                  ,MORA
        100752764,403004,1,20151208,03731,EZEQUIEL                      ,LEON                      ,CALVO
        100753244,210012,2,20161009,02599,CONSTANCIA                    ,ARIAS                     ,RIVERA
        100753335,115001,2,20180211,01362,MARGARITA                     ,ALVARADO                  ,LAHMAN
        100753618,111005,2,20220109,01168,ETELVINA                      ,PARRA                     ,SALAZAR
        100763791,108007,1,20190831,00971,REINALDO                      ,MENDEZ                    ,BARBOZA

    - It lists all the voters in Costa Rica: their id, voting district,
      officialy sex (as if anyone should care), id expiration, voting site,
      name, first family name and second family name.
    - It is encoded in ``ISO-8859-15`` and uses Windows CRLF line terminators.
    - It is quite unstable. Deaths and people passing 18 years are removed -
      added.
    - It is very large. As this writting, the CSV file is 364MB in size, with
      3 178 364 lines (and thus, registered voters).
    - The semantics of the sex code is as following: ``1``: men, ``2``: women.
    - The format of the id expiration date is ``%Y%m%d`` as following:

      ::

          <year(4 digit)><month(2 digits)><day(2 digits)>

    This class will interpret the file on the fly without loading it entirely
    on main memory.
    Also, the file will be processed even if some lines are malformed. Any
    error will be logged as such.
    """  # noqa

    def __init__(self, search_dir, distelec):
        self.total_voters = None
        self._search_dir = search_dir
        self._distelec = distelec
        self._filename = get_file(search_dir, 'PADRON_COMPLETO.txt')
        self._bad_data = []
        self._voters_file = None
        self._voters_iter = None

    def open(self):
        """
        Open voters file for on-the-fly parsing.
        """
        self.total_voters = count_lines(self._filename)
        self._voters_file = open_with_encoding(
            self._filename, 'rb', 'iso8859-15'
        )
        self._voters_iter = enumerate(self._voters_file, 1)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            linenum, line = next(self._voters_iter)

            line = line.strip()
            if not line:
                log.warning(
                    'PADRON_COMPLETO.txt :: Ignoring empty line #{}'.format(
                        linenum
                    )
                )
                continue

            try:
                # Parse line
                parts = line.split(',')
                assert len(parts) == 8
                parsed = {
                    'id': int(parts[0]),
                    'district': int(parts[1]),
                    'sex': int(parts[2]),
                    'expiration': datetime.strptime(parts[3], '%Y%m%d').date(),
                    'site': int(parts[4]),
                    'name': titleize(
                        parts[5].strip().replace("'", "\\'")
                    ),
                    'family_name_1': titleize(
                        parts[6].strip().replace("'", "\\'")
                    ),
                    'family_name_2': titleize(
                        parts[7].strip().replace("'", "\\'")
                    ),
                }

                # Validate district code
                district_code = parsed['district']
                district_key = (
                    district_code // 100000,
                    (district_code % 100000) // 1000,
                    district_code % 1000
                )
                assert district_key in self._distelec.districts

                # FIXME: Shall we perform some other assert here to validate
                # data?

                return parsed

            except Exception:
                self._bad_data.append(linenum)
                log.error(
                    'PADRON_COMPLETO.txt :: Bad data at line #{}:\n{}'.format(
                        linenum, line
                    )
                )
                log.debug(format_exc())
                continue


__all__ = ['DistrictsReader', 'VotersReader']
