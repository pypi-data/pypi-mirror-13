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

import sys
import logging
from getpass import getuser
from os import makedirs
from tempfile import TemporaryDirectory

import hcpcbc


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    # collect the command line options
    opts = hcpcbc.parseargs()

    # Read and parse the config file
    try:
        conf = hcpcbc.Config(opts.ini)
    except hcpcbc.HcpcbcError as e:
        sys.exit(e)

    logger = logging.getLogger(__name__)

    # update the config with a fresh list of available tenants
    if not opts.chartsonly:
        try:
            if not hcpcbc.updatetenants():
                logger.critical('wasn\'t able to access any HCP system - aborting')
                sys.exit(1)
        except Exception as e:
            logger.exception('updatetenants() failed\n\thint: {}'.format(e))
            sys.exit(1)
    else:
        logger.info('skipping the Tenant list(s) update')


    # if the -u flag has been set, update the Tenant list(s), only!
    if not opts.update:

        # Create a temporary store
        try:
            makedirs(hcpcbc.Ivars.conf['3 stores']['1 temporary']['1 tempdir'],
                     exist_ok=True)
            tmpstore = TemporaryDirectory(
                    dir=hcpcbc.Ivars.conf['3 stores']['1 temporary'][
                        '1 tempdir'],
                    suffix='.cbc')
        except KeyError as e:
            logger.error(
                    'parsing the config file failed:\n\thint: {}'.format(e))
            sys.exit(1)

        logger.debug('Using temporary store at "{}"'.format(tmpstore.name))

        try:
            # make sure we don't collect new reports if the '-c' flag is given
            if opts.chartsonly:
                logger.info('skipping report download')
            else:
                #   Loop over all configured HCP systems
                handlers = {}  # used to store all the handlers we'll create
                for target, idx in zip(hcpcbc.Ivars.conf['1 targets'],
                                       range(0,
                                             len(hcpcbc.Ivars.conf[
                                                     '1 targets']))):
                    # make sure we don't process targets that don't have any Tenants
                    if target['9 tenants']:
                        logger.info('working on target "{}" (idx={})'
                                    .format(target['1 fqdn'], idx))
                        handlers[target['1 fqdn']] = {}

                        # Now, let's create hcpsdk.cbhandler.Handler() objects for
                        # each Tenant
                        for tenant in target['9 tenants'].keys():
                            # skip Tenants that are disabled from collection
                            if not target['9 tenants'][tenant][
                                '0 enable collection']:
                                logger.info(
                                        '\tskipping Tenant "{}"'.format(
                                            tenant))
                                continue
                            else:
                                logger.info(
                                        '\tcollecting from Tenant "{}"'.format(
                                                tenant))

                            handler = hcpcbc.Handler(idx, tenant, tmpstore,
                                                     opts.pastdays)
                            handler.download()
                            handler.dissect()
                            if hcpcbc.Ivars.conf['3 stores']['2 local'][
                                '1 enable']:
                                handler.transferlocal()
                            if hcpcbc.Ivars.conf['3 stores']['3 compliant'][
                                '1 enable']:
                                handler.transfercompliant()

                            handler.close()
                    else:
                        logger.warning(
                            'target "{}" (idx={}) has no Tenants listed'
                            .format(target['1 fqdn'], idx))

            # now create charts from the data available
            try:
                if hcpcbc.Ivars.conf['4 charts'][
                    '1 enable'] or opts.chartsonly:
                    hcpcbc.mkcharts(tmpstore.name)
            except Exception as f:
                logger.error('\tchart creation failed\n\thint: {}'.format(f))

        except KeyError as e:
            logger.error(
                    'parsing the config file failed:\n\thint: {}'.format(e))

        # remove the temporary store
        tmpstore.cleanup()

    # re-save the configfile
    try:
        conf.save()
    except hcpcbc.HcpcbcError as e:
        logger.error('failed to re-write the configfile\n\thint: {}'
                     .format(getuser(), e))

    logger.info('finished run (user "{}")\n'.format(getuser()))


if __name__ == '__main__':
    main()
