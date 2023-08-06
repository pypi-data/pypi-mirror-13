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
TSE voting center data scrapper module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from json import dumps
from logging import getLogger
from traceback import format_exc
from collections import OrderedDict

from tqdm import tqdm
from requests import post
from inflection import titleize, humanize
from six.moves.urllib.parse import urlparse, parse_qs


log = getLogger(__name__)


SCRAPPER_URL = (
    'http://www.tse.go.cr/DondeVotarM/prRemoto.aspx/ObtenerDondeVotar'
)


def parse_location(url):
    """
    Parse latitude and longitude from a Google Maps URL.
    """
    params = parse_qs(urlparse(url).query, keep_blank_values=True)
    if 'll' in params:
        return tuple(float(c) for c in params.get('ll')[0].split(','))
    return (0.0, 0.0)


def scrappe_data(samples):
    """
    Scrapper main function.

    :param dict samples: A dictionary with the ids samples.
    :return: A dictionary with the scrapped data of the form.
    :rtype: dict
    """

    headers = {'Content-Type': 'application/json'}
    scrapped_data = OrderedDict()

    with tqdm(
            total=len(samples), unit='r',
            leave=True, desc='POST requests') as pbar:

        # Iterate samples to grab data from web service
        for district, id_voter in samples.items():
            payload = dumps({'numeroCedula': str(id_voter)})

            retries = 5
            while retries > 0:

                try:
                    response = post(
                        SCRAPPER_URL,
                        headers=headers,
                        data=payload
                    )
                    response.raise_for_status()

                    data = response.json()['d']['lista']

                    latitude, longitude = parse_location(data['url'])
                    address = humanize(
                        data['direccionEscuela'].strip().lower()
                    )
                    name = titleize(
                        data['nombreCentroVotacion'].strip().lower()
                    )

                    # Record data
                    scrapped_data[district] = {
                        'latitude': latitude,
                        'longitude': longitude,
                        'address': address,
                        'name': name
                    }

                    pbar.update(1)
                    break
                except:
                    log.error(
                        'Error while processing district #{} '
                        'using voter id #{} :: (RETRIES LEFT: {})\n{}'.format(
                            district, id_voter, retries, format_exc()
                        )
                    )

                retries -= 1

    return scrapped_data


__all__ = ['scrappe_data']
