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
Application entry point module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from json import dumps
from logging import getLogger
from datetime import datetime

from .utils import is_url, download, sha256, unzip
from .readers import DistrictsReader, VotersReader
from .render import list_renderers, render


log = getLogger(__name__)


def main(args):
    """
    Application main function.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`
    :return: Exit code.
    :rtype: int
    """
    start = datetime.now()
    log.debug('Start timestamp: {}'.format(start.isoformat()))

    # Download archive if required
    archive = args.archive
    if is_url(archive):
        archive = download(archive, subdir='tse2sql')

    # Calculate digest and unzip archive
    digest = sha256(archive)
    extracted = unzip(archive)

    # Parse distelec file
    distelec = DistrictsReader(extracted)
    distelec.parse()

    # Save analysis file
    analysis = dumps(distelec.analyse(), sort_keys=True, indent=4)
    log.info('Distelec analysis:\n{}'.format(analysis))
    with open('{}.data.json'.format(digest), 'w') as fd:
        fd.write(analysis)

    # Open voters file
    voters = VotersReader(extracted, distelec)
    voters.open()

    # Get list of renderers to use
    if args.renderer is None:
        renderers = list_renderers()
    else:
        renderers = [args.renderer]

    # Build rendering payload
    payload = {
        'digest': digest,
        'provinces': distelec.provinces,
        'cantons': distelec.cantons,
        'districts': distelec.districts,
        'voters': voters
    }

    # Generate SQL output
    for rdr in renderers:
        print('Writing output for {} ...'.format(rdr))
        with open('{}.{}.sql'.format(digest, rdr), 'w') as sqlfile:
            render(payload, rdr, sqlfile)

    # Log elapsed time
    end = datetime.now()
    print('Elapsed time: {}s'.format((end - start).seconds))

    return 0


__all__ = ['main']
