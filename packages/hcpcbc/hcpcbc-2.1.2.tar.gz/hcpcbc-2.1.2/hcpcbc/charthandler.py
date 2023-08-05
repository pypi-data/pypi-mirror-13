#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2012-2016 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Sos of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyrighftware without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copiet notice and this permission notice shall be included in
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
from os import makedirs
from os.path import join
from time import strftime, localtime
import hcpcbc
import charts

logging.getLogger('hcpcbc.charthandler').addHandler(logging.NullHandler())


def mkcharts(tmpdir):
    """
    Create charts from the locally stored reports.

    Args:
        tmpdir:     the temporary folder

    """
    logger = logging.getLogger(__name__)
    logger.debug('now creating charts')

    modes = []
    if hcpcbc.Ivars.conf['4 charts']['3 hourly charts']:
        modes.append(charts.M_HOUR)
    if hcpcbc.Ivars.conf['4 charts']['6 daily charts']:
        modes.append(charts.M_DAY)
    if not len(modes):
        raise charts.ChartsError('neither daily or hourly charts enabled')

    # create a standard filename for the xlsx files created
    # and make sure we don't have colons in the name, as the conflict with
    # Windows :-(
    outnamepostfix = strftime(hcpcbc.Ivars.timeformatwoz, localtime()).replace(
        ':', '-')

    # working on the configured HCP systems
    for target, idx in zip(hcpcbc.Ivars.conf['1 targets'],
                           range(0, len(hcpcbc.Ivars.conf['1 targets']))):
        logger.info('creating charts for HCP "{}"'.format(
                hcpcbc.Ivars.conf['1 targets'][idx]['1 fqdn']))

        # creating charts per Tenant (Namespaces comparison):
        for tenant in hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'].keys():
            logger.info('\tworking on Tenant "{}"'.format(tenant))

            for mode in modes:
                logger.debug('\t\tworking "{}"'.format(mode))
                data = charts.prep.prepdata(join(
                        hcpcbc.Ivars.conf['3 stores']['2 local']['2 path'],
                        hcpcbc.Ivars.conf['1 targets'][idx]['4 folder'],
                        tenant),
                        tenant=tenant,
                        startdate=None,
                        enddate=None,
                        mode=mode)
                outpath = join(hcpcbc.Ivars.conf['4 charts']['2 path'],
                               hcpcbc.Ivars.conf['1 targets'][idx]['4 folder'],
                               tenant, '__charts', mode)
                makedirs(outpath, exist_ok=True)
                chdl = charts.xlsx.Handler(
                        join(outpath,
                             '.'.join([tenant, outnamepostfix, 'xlsx'])),
                        tmpdir,
                        hcpcbc.Ivars.conf['1 targets'][idx]['1 fqdn'],
                        tenantname=tenant, mode=mode)
                chdl.genxlsx(data)
                chdl.gencharts(abs=hcpcbc.Ivars.conf['4 charts']['a linear'],
                               log=hcpcbc.Ivars.conf['4 charts']['b log'])
                chdl.close()

        # creating charts with Tenant comparison
        logger.info('\tworking on Tenant comparison charts')
        for mode in modes:
            logger.debug('\t\tworking "{}"'.format(mode))
            data = charts.prep.prepdata(join(
                    hcpcbc.Ivars.conf['3 stores']['2 local']['2 path'],
                    hcpcbc.Ivars.conf['1 targets'][idx]['4 folder']),
                    tenant=None,
                    startdate=None,
                    enddate=None,
                    mode=mode)
            outpath = join(hcpcbc.Ivars.conf['4 charts']['2 path'],
                           hcpcbc.Ivars.conf['1 targets'][idx]['4 folder'],
                           '__system', '__charts', mode)
            makedirs(outpath, exist_ok=True)
            chdl = charts.xlsx.Handler(
                    join(outpath, '.'.join([outnamepostfix, 'xlsx'])),
                    tmpdir,
                    hcpcbc.Ivars.conf['1 targets'][idx]['1 fqdn'],
                    tenantname=None, mode=mode)
            chdl.genxlsx(data)
            chdl.gencharts(abs=hcpcbc.Ivars.conf['4 charts']['a linear'],
                           log=hcpcbc.Ivars.conf['4 charts']['b log'])
            chdl.close()
