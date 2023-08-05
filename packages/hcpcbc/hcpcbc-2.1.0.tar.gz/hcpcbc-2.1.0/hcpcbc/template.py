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

from sys import platform

if platform == 'win32':
    tmppath = '.\\_hcpcbc.dir'
    lclpath = '.\\_hcpcbc.dir'
    chtpath = '.\\_hcpcbc.charts'
    logpath = '.\\_hcpcbc.dir\\_hcpcbc.log'
else:
    tmppath = './_hcpcbc.dir'
    lclpath = './_hcpcbc.dir'
    chtpath = './_hcpcbc.charts'
    logpath = './_hcpcbc.dir/_hcpcbc.log'




template = {'0 comment': ['This it the configuration file for **hcpcbc**. For a detailed',
                          'description visit *https://hcpcbc.readthedocs.org*.'],
            '1 targets': [{'0 comment': ['An HCP system to collect from. *User* needs to be a',
                                         'system-level user that has the *Monitor* role enabled.'],
                           '1 fqdn': 'hcp72.archivas.com',
                           '2 user': 'monitor',
                           '3 password': 'monitor01',
                           '4 folder': 'hcp72',
                           '9 tenants': {}
                           },
                          {'0 comment': ['An HCP system to collect from. *User* needs to be a',
                                         'system-level user that has the *Monitor* role enabled.'],
                           '1 fqdn': 'hcp73.archivas.com',
                           '2 user': 'monitor',
                           '3 password': 'monitor01',
                           '4 folder': 'hcp73',
                           '9 tenants': {}
                           },
                          ],
            '2 parameters': {'0 comment': ['*1 periode* defines the reports granularity,',
                                           '*2 collection limit* defines for how many days collection',
                                           'takes place, starting from the last collection time.',
                                           '*3 timeout* defines the tcp connection timeout'],
                             '1 periode': ['total','day','hour'],
                             '2 collection limit': 181,
                             '3 timeout': 600},
            '3 stores': {'1 temporary': {'0 comment': ['The temporary directory in which the downloaded',
                                                       'reports are stored during processing.'],
                                         '1 tempdir': tmppath},
                         '2 local': {'0 comment': ['The directory in which processed reports are',
                                                   'stored locally.'],
                                     '1 enable': True,
                                     '2 path': lclpath,
                                     '9 store raw': True},
                         '3 compliant': {'0 comment': ['This is the HCP Namespace to which the processed reports',
                                                       'can be stored for long-term preservation'],
                                         '1 enable': False,
                                         '2 path': 'https://n1.m.hcp72.archivas.com/rest/chargeback',
                                         '3 user': 'n',
                                         '4 password': 'n01',
                                         '5 retention': '0',
                                         '9 store raw': True},
                         },
            '4 charts': {'0 comment': ["Chart creation",
                                       "*hourly charts* will use the hour reports to create charts",
                                       "*daily charts* will do the same using the day reports."],
                         '1 enable': True,
                         '2 path': chtpath,
                         '3 hourly charts': True,
                         '6 daily charts': True,
                         'a linear': True,
                         'b log': True
            },
            '9 logging': {'0 comment': ['This defines how hcpcbc does logging.'],
                          '1 log to stdout': True,
                          '2 log to file': False,
                          '3 logfile': logpath,
                          '4 rotate MB': 10,
                          '5 backups': 9,
                          '6 debug': False}
            }
