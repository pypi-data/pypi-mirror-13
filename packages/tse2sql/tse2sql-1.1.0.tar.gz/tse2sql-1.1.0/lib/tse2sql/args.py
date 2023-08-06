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
Argument management module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

import logging
from os.path import isfile, abspath

from . import __version__
from .utils import is_url
from .render import list_renderers
from .readers import REGISTRY_URL


log = logging.getLogger(__name__)


FORMAT = '%(asctime)s:::%(levelname)s:::%(message)s'
V_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


def validate_args(args):
    """
    Validate that arguments are valid.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`
    :return: The validated namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    level = V_LEVELS.get(args.verbose, logging.DEBUG)
    logging.basicConfig(format=FORMAT, level=level)

    log.debug('Raw arguments:\n{}'.format(args))

    # Verify input file exists
    if not is_url(args.archive):
        if not isfile(args.archive):
            log.error('No such file : {}'.format(args.archive))
            exit(1)
        args.archive = abspath(args.archive)

    return args


def validate_args_scrapper(args):
    """
    Validate that arguments are valid for the scrapper.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`
    :return: The validated namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    level = V_LEVELS.get(args.verbose, logging.DEBUG)
    logging.basicConfig(format=FORMAT, level=level)

    log.debug('Raw arguments:\n{}'.format(args))

    # Verify samples file exists
    if not is_url(args.samples):
        if not isfile(args.samples):
            log.error('No such file : {}'.format(args.samples))
            exit(1)
        args.samples = abspath(args.samples)

    return args


def parse_args(argv=None):
    """
    Argument parsing routine.

    :param argv: A list of argument strings.
    :rtype argv: list
    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=(
            'SQL converter of the electoral registry published by the Costa '
            'Rican Supreme Electoral Tribunal.'
        )
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Increase verbosity level',
        default=0,
        action='count'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Convertidor del Padron Electoral a SQL v{}'.format(
            __version__
        )
    )

    parser.add_argument(
        '--renderer',
        default=None,
        help='SQL renderer to use',
        choices=list_renderers()
    )

    parser.add_argument(
        'archive',
        nargs='?',
        help='URL or path to the voters database',
        default=REGISTRY_URL
    )

    args = parser.parse_args(argv)
    args = validate_args(args)
    return args


def parse_args_scrapper(argv=None):
    """
    Scrapper argument parsing routine.

    :param argv: A list of argument strings.
    :rtype argv: list
    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(description=('TSE Voting Sites Scrapper'))

    parser.add_argument(
        '-v', '--verbose',
        help='Increase verbosity level',
        default=0,
        action='count'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='TSE Voting Sites Scrapper v{}'.format(
            __version__
        )
    )

    parser.add_argument(
        '--renderer',
        default=None,
        help='SQL renderer to use',
        choices=list_renderers()
    )

    parser.add_argument(
        'samples',
        help='Samples file with one id number per site id'
    )

    args = parser.parse_args(argv)
    args = validate_args_scrapper(args)
    return args


__all__ = ['parse_args', 'parse_args_scrapper']
