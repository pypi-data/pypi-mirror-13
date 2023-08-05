# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2012-2016 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import logging
from csv import DictReader
from os.path import join
# workaround to allow documentation to be built below Python 3.5
try:
    from os import scandir
except ImportError:
    scandir = print
from . import M_DAY, M_HOUR, M_ALL, rec, S_SPECIALFOLDERS

logging.getLogger('charts.prep').addHandler(logging.NullHandler())


def prepdata(path, tenant=None, startdate=None, enddate=None, mode=M_DAY):
    """
    Create a data structure holding an HCPs summary chargeback data of all
    available Tenants or Namespaces. Reads a source folder structure created by
    **hcpcbc**.

    struct = {startdate (-> datetime): {"item_a": record (--> rec),
                                        "item_b": record(--> rec),
                                        "item_z": record(--> rec),}}

    Args:
        path:       the path under which the report files are stored
        tenant:     Tenant name or None if working on system level
        startdate:  a datetime object
        enddate:    a datetime object
        mode:       one of [M_DAY, M_HOUR]

    Returns:    the mentioned structure
    """
    logger = logging.getLogger(__name__)
    logger.debug('preparing data from "{}"'.format(path))

    if mode not in [M_DAY, M_HOUR]:
        raise ValueError('mode must be one of {}'.format([M_DAY, M_HOUR]))

    # create the result structure (dict)
    res = {}

    # Get a list of items (Tenants or Namespaces)
    items = []
    for entry in scandir(path):
        if not tenant and not entry.name.startswith('.') and entry.is_dir():
            # --> working on system level
            items.append(entry.name)
        elif tenant and not entry.name.startswith(
                '.') and entry.is_dir() and entry.name not in S_SPECIALFOLDERS:
            # --> working on tenant level
            items.append(entry.name)
        else:
            logger.debug('invalid entry "{}" in path "{}"'.format(entry.name,
                                                                    path))

    logger.debug('Items: {}'.format(items))

    # Crawl through all Tenants to collect report data
    for t in items:
        # Get a list of reports
        reports = []
        if not tenant:
            tpath = join(path, t, '__tenant', mode)
        else:
            tpath = join(path, t, mode)
        try:
            for entry in scandir(tpath):
                if not entry.name.startswith('.') and entry.is_file():
                    reports.append(entry.name)
        except FileNotFoundError:
            logger.debug('folder not available: "{}"'.format(tpath))
            continue
        reports.sort()
        logger.debug('\tReports for {}:'.format(t))
        for rep in reports:
            logger.debug('\t\t{}'.format(rep))

        # loop over the found reports and fill the result structure
        for rep in reports:
            with open(join(tpath, rep)) as csvhdl:
                reader = DictReader(csvhdl)
                for r in reader:
                    if (mode == M_DAY and r['startTime'][11:19] == '00:00:00' \
                                and  r['endTime'][11:19] == '23:59:59') or \
                       (mode == M_HOUR and r['startTime'][14:19] == '00:00' \
                                and  r['endTime'][14:19] == '59:59'):
                        thisrec = rec(r['objectCount'],
                                      r['ingestedVolume'],
                                      r['storageCapacityUsed'],
                                      r['bytesIn'], r['bytesOut'], r['reads'],
                                      r['writes'], r['deletes'],
                                      r['tieredObjects'],
                                      r['tieredBytes'],
                                      r['metadataOnlyObjects'],
                                      r['metadataOnlyBytes'], r['deleted'],
                                      r['valid'])
                        try:
                            res[r['startTime']][t] = thisrec
                        except KeyError:
                            res[r['startTime']] = {}
                            res[r['startTime']][t] = thisrec
                    else:
                        logger.debug('\t\tdropped: {} - {}'
                                     .format(r['startTime'], r['endTime']))

    return res
