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
import hcpsdk
from pprint import pprint
from time import sleep

from .init import Ivars
#from . import HcpcbcError

def updatetenants():
    '''
    Get a list of Tenants from all configured HCP systems and update the config
    object accordingly, if required.

    :return:    True if at least one HCP system could be accessed, False if
                all went wrong
    :raises:    HcpcbcError() in case of any fatal failure
    '''
    logger = logging.getLogger(__name__)
    success = False
    _targets = []
    for hcp in Ivars.conf['1 targets']:
        logger.info('updating the Tenant list for "{}"'
                     .format(hcp['1 fqdn']))

        auth = hcpsdk.NativeAuthorization(hcp['2 user'], hcp['3 password'])

        try:
            tgt = hcpsdk.Target('.'.join(['admin', hcp['1 fqdn']]), auth,
                                         port=hcpsdk.P_MAPI)
        except Exception as e:
            logger.warning('Creating target for "{}" failed\n\thint: {}'
                           .format(hcp['1 fqdn'], e))
        else:
            try:
                tenants = hcpsdk.mapi.listtenants(tgt,
                                                  timeout=
                                                  Ivars.conf['2 parameters']
                                                            ['3 timeout'])
            except Exception as e:
                logger.warning('listtenants() for "{}" failed\n\thint: {}'
                               .format(hcp['1 fqdn'], e))
            else:
                success = True
                for tenant in tenants:
                    t = tenant.info()
                    try:
                        tname = t['name']
                    except KeyError as e:
                        logger.warning('\tDefault Tenant found - no chargeback '
                                       'support')
                        tenant.close()
                        continue
                    newrec = {t['name']:
                                  {'1 adminAllowed':
                                       t.get('administrationAllowed', False),
                                   '2 user': '',
                                   '3 password': '',
                                   '4 systemVisibleDescription':
                                       t.get('systemVisibleDescription', ""),
                                   '9 last collected': ''
                                             }}
                    # Now in case this Tenant has not adminAllowed enabled,
                    # let's check if we had this Tenant already and if the
                    # user added credentials in the past
                    if not newrec[t['name']]['1 adminAllowed']:
                        if t['name'] in hcp['9 tenants'].keys():
                            newrec[t['name']]['2 user'] = \
                                hcp['9 tenants'][t['name']]['2 user']
                            newrec[t['name']]['3 password'] = \
                                hcp['9 tenants'][t['name']]['3 password']
                    # preserve the last collection date, if it exists
                    try:
                        if hcp['9 tenants'][t['name']]['9 last collected']:
                            newrec[t['name']]['9 last collected'] = \
                                hcp['9 tenants'][t['name']]['9 last collected']
                    except KeyError:
                        logger.debug('Tenant "{}" not yet in configfile'
                                     .format(t['name']))

                    hcp['9 tenants'].update(newrec)
                    tenant.close()

        _targets.append(hcp)

    sleep(.5)
    Ivars.conf['1 targets'] = _targets

    return success



