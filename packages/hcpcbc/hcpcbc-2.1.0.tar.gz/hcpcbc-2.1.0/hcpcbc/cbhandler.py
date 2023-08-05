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

import sys
from datetime import datetime, timedelta
from shutil import copyfile
from pathlib import Path
from os import makedirs, rename
from os.path import join, dirname
from csv import DictReader
from urllib.parse import urlparse
import logging
import hcpsdk
import hcpcbc


class Handler(object):
    """
    A class that handles the chargeback report download for a single HCP target
    """

    def __init__(self, idx, tenant, tempstore):
        """
        Initialize communication to an HCP system

        :param idx:         the index of the HCP in charge in Ivars.conf['1 targets]
        :param tenant:      the Tenants name from this HCP
        :param tmpstore:    an instance of the Temporarystore() class
        """
        self.logger = logging.getLogger(__name__ + '.Handler')
        self.logger.debug('Handler initializing for {}'
                          .format('.'.join([tenant,
                                            hcpcbc.Ivars.conf['1 targets'][
                                                idx]['1 fqdn']])))
        self.idx = idx
        self.tenant = tenant
        self.tempstore = tempstore
        self.rawfiles = []  # list of raw report files got from HCP
        self.cookedfiles = []  # list of cooked files (per Tenant, Namespace)

        # find out if the Tenant has granted access for system-level users'
        # and create the proper FQDN and Authorization object
        self.fqdn = '.'.join(
                [tenant, hcpcbc.Ivars.conf['1 targets'][idx]['1 fqdn']])

        if hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
            '1 adminAllowed'] or \
                (not hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
                    '1 adminAllowed'] and \
                         not hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][
                             tenant]['2 user']):
            if not hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
                '1 adminAllowed'] and \
                    not \
                    hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
                        '2 user']:
                self.logger.info('\t--> unable to collect namespace details')
            self._fqdn = '.'.join(['admin',
                                   hcpcbc.Ivars.conf['1 targets'][idx][
                                       '1 fqdn']])
            auth = hcpsdk.NativeAuthorization(
                    hcpcbc.Ivars.conf['1 targets'][idx]['2 user'],
                    hcpcbc.Ivars.conf['1 targets'][idx]['3 password'])
        else:
            self._fqdn = self.fqdn
            auth = hcpsdk.NativeAuthorization(
                    hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
                        '2 user'],
                    hcpcbc.Ivars.conf['1 targets'][idx]['9 tenants'][tenant][
                        '3 password'])

        # Open the session with HCP
        try:
            self.logger.debug(
                'Using FQDN: {} (self.tenant = "{}"'.format(self._fqdn,
                                                            self.tenant))
            self.t = hcpsdk.Target(self._fqdn, auth, port=hcpsdk.P_MAPI)
            self.cb = hcpsdk.mapi.Chargeback(self.t, timeout=
            hcpcbc.Ivars.conf['2 parameters']
            ['3 timeout'],
                                             debuglevel=0)
        except Exception as e:
            raise hcpcbc.HcpcbcError('Connection to {} failed\n\thint: {}'
                                     .format(self.tgt['fqdn'], e))

    def download(self):
        """
        Download the chargeback report from HCP
        """
        self.logger.debug('downloading for {}'.format(self.fqdn))

        # Timeframes: 2015-12-02T13:28:41+0100 - 2015-12-12T18:29:04+0100

        # Calculate the required datetimes:
        self.logger.debug('\tlast collected = {}'
                          .format(hcpcbc.Ivars.conf['1 targets'][self.idx] \
                                      ['9 tenants'][self.tenant] \
                                      ['9 last collected']))
        if hcpcbc.Ivars.conf['1 targets'][self.idx]['9 tenants'][self.tenant] \
                ['9 last collected']:
            try:
                starttime = datetime.strptime(
                        hcpcbc.Ivars.conf['1 targets'][self.idx]
                        ['9 tenants'][self.tenant]
                        ['9 last collected'],
                        hcpcbc.Ivars.timeformat)
                # we may get a value without the Timezone included, in which
                # case we fail here and give it another try with a different
                # format in the except clause:
            except ValueError:
                starttime = datetime.strptime(
                        hcpcbc.Ivars.conf['1 targets'][self.idx]
                        ['9 tenants'][self.tenant]
                        ['9 last collected'],
                        hcpcbc.Ivars.timeformatwoz)

        else:
            starttime = datetime.now() - timedelta(days=181, seconds=1)

        endtime = starttime + timedelta(
            days=hcpcbc.Ivars.conf['2 parameters']['2 collection limit'])

        for granularity in hcpcbc.Ivars.conf['2 parameters']['1 periode']:
            try:
                if granularity == hcpsdk.mapi.Chargeback.CBG_TOTAL:
                    report = self.cb.request(tenant=self.tenant,
                                             granularity=granularity,
                                             fmt=hcpsdk.mapi.Chargeback.CBM_CSV)
                else:
                    report = self.cb.request(tenant=self.tenant,
                                             start=starttime,
                                             end=endtime,
                                             granularity=granularity,
                                             fmt=hcpsdk.mapi.Chargeback.CBM_CSV)
            except Exception as e:
                if str(e).startswith('403'):
                    if self.fqdn.startswith('admin'):
                        hint = '\n\thint: MAPI disabled for Tenant?!?'
                    else:
                        hint = '\n\thint: no access permission'
                elif str(e).startswith('503'):
                    hint = '\n\thint: MAPI disabled for Tenant?!?'
                else:
                    hint = ''
                self.logger.warning('\tdownload from {} failed\n\thint: {}{}'
                                    .format(self.fqdn, e, hint))

            # find startTime and enTime for the entire report
            reader = DictReader(report)
            _start = _end = None
            for rec in reader:
                if not rec['namespaceName']:
                    if not _start:
                        _start = rec['startTime']
                    _end = rec['endTime']
            self.logger.debug('\t{} report for "{}": start {}, end {}'
                                .format(granularity, self.tenant, _start,
                                        _end))

            if not _end:    # we havem't got any data...
                self.logger.debug('\tno "{}" report for "{}"'
                                  .format(granularity, outpath))
                # ...so we record the actual endtime as last collected...
                # as we need to record the time of last collection,
                # this is true only for 'day' and 'hour', but not for 'total'
                if granularity != hcpsdk.mapi.Chargeback.CBG_TOTAL:
                    hcpcbc.Ivars.conf['1 targets'][self.idx][
                        '9 tenants'] \
                        [self.tenant]['9 last collected'] = \
                        endtime.strftime(hcpcbc.Ivars.timeformat)
            else:
                outpath = join(self.tempstore.name,
                               '.'.join([granularity, self.fqdn,
                                         '_'.join([_start, _end])])).replace(':', '-')
                self.logger.debug('\treport will be stored to "{}"'
                                  .format(outpath))
                try:
                    with open(outpath, 'w') as outhdl:
                        report.seek(0)  # rewind
                        outhdl.write(report.read())
                        # as we need to record the time of last collection,
                        # this is true only for 'day' and 'hour', but not for
                        # 'total'
                        if granularity != hcpsdk.mapi.Chargeback.CBG_TOTAL:
                            hcpcbc.Ivars.conf['1 targets'][self.idx][
                                '9 tenants'] \
                                [self.tenant]['9 last collected'] = _end

                    self.rawfiles.append(outpath)
                except Exception as e:
                    self.logger.error('\twrite of {} failed\n\thint: {}'
                                        .format(outpath, e))

    def dissect(self):
        '''
        Dissect the raw report into separate files (one per Namespace plus
        one holding the Tenant's summaries.
        '''
        for rawfile in self.rawfiles:
            self.logger.debug('rawfile = {}'.format(rawfile))
            if sys.platform == 'win32':
                _raw = rawfile.split('\\')[-1]
            else:
                _raw = rawfile.split('/')[-1]
            if _raw.startswith(hcpsdk.mapi.Chargeback.CBG_DAY):
                self.logger.debug('mode = {}'.format(hcpsdk.mapi.Chargeback.CBG_DAY))
                mode = hcpsdk.mapi.Chargeback.CBG_DAY
            elif _raw.startswith(hcpsdk.mapi.Chargeback.CBG_HOUR):
                self.logger.debug('mode = {}'.format(hcpsdk.mapi.Chargeback.CBG_HOUR))
                mode = hcpsdk.mapi.Chargeback.CBG_HOUR
            elif _raw.startswith(hcpsdk.mapi.Chargeback.CBG_TOTAL):
                self.logger.debug('mode = {}'.format(hcpsdk.mapi.Chargeback.CBG_TOTAL))
                mode = hcpsdk.mapi.Chargeback.CBG_TOTAL
            else:
                self.logger.debug('mode = invalid\n\thint: rawfile = {}'
                                  .format(rawfile))
                continue
            self.logger.debug('\tdissecting {}'.format(_raw))

            # systemName,tenantName,namespaceName,startTime,endTime,
            # objectCount,ingestedVolume,storageCapacityUsed,bytesIn,bytesOut,
            # reads,writes,deletes,tieredObjects,tieredBytes,
            # metadataOnlyObjects,metadataOnlyBytes,deleted,valid
            # hcp72.archivas.com,m,n1,2015-12-17T00:00:00+0100,
            # 2015-12-17T23:59:59+0100,7219,25303387299,25306468352,0,0,0,0,0,
            # 7219,25303387299,0,0,false,true

            try:
                with open(rawfile, 'r') as inhdl:
                    # read header and first row
                    headerline = inhdl.readline()
                    row = inhdl.readline().strip().split(',')
                    tenant = row[1]     # the Tenant we're working on
                    namespace = None    # the actual Namespace
                    outhdl = None       # handle to output file
                    endTime = None      # the latest endTime seen

                    while row:
                        try:
                            if row[2] != namespace:
                                namespace = row[2]
                                if outhdl:
                                    outhdl.close()
                                    _outname = '{}_{}'\
                                        .format(outname, endTime.replace(':','-'))
                                    rename(outname, _outname)
                                    self.cookedfiles.append(_outname)
                                try:
                                    if row[2]:
                                        tgtdir = join(self.tempstore.name,
                                                      hcpcbc.Ivars.conf[
                                                          '1 targets'][
                                                          self.idx][
                                                          '4 folder'],
                                                      row[1], row[2], mode)
                                    else:
                                        tgtdir = join(self.tempstore.name,
                                                      hcpcbc.Ivars.conf[
                                                          '1 targets'][
                                                          self.idx][
                                                          '4 folder'],
                                                      row[1], '__tenant', mode)
                                    makedirs(tgtdir, exist_ok=True)
                                except Exception as e:
                                    self.logger.error(
                                        'failed to create folder {}\n\thint: {}'
                                        .format(
                                            join(self.tempstore.name, row[0]),
                                            e))
                                    outhdl = None
                                    continue

                                outname = join(tgtdir, row[3].replace(':', '-'))
                                try:
                                    outhdl = open(outname, 'w')
                                    outhdl.write(headerline)
                                except Exception as e:
                                    self.logger.warning('\topen of {} failed'
                                                        '\n\t\thint: {}'
                                                        .format(outname, e))
                                else:
                                    self.logger.debug(
                                        '\twriting {}'.format(outname))
                            if outhdl:
                                outhdl.write(','.join(row) + '\n')
                        except IndexError:
                            self.logger.debug('\treached end of file')
                            if outhdl:
                                outhdl.close()
                                _outname = '{}_{}'\
                                    .format(outname,endTime.replace(':', '-'))
                                rename(outname, _outname)
                                self.cookedfiles.append(_outname)
                            break
                        endTime = row[4]
                        row = inhdl.readline().strip().split(',')
            except FileNotFoundError as e:
                self.logger.debug('\tfile not found: {} ({})'
                                  .format(rawfile, e))

    def transferlocal(self):
        '''
        Transfer all generated files to the local store.
        '''
        self.logger.info('\ttranfering reports to local store')

        if hcpcbc.Ivars.conf['3 stores']['2 local']['9 store raw']:
            # self.rawfiles = [
            #     './_hcpcbc.dir/tmp84dcd92l.cbc/total.s3erlei.hcp72.archivas.\
            #    com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100',]
            for copysrc in self.rawfiles:
                self.logger.debug('copysrc = {}'.format(copysrc))
                try:
                    base = copysrc.split(join(self.tempstore.name, ''))
                    # (the join() adds a trailing folder delimiter (/ or \)
                    # copyysrc = './_hcpcbc.dir/tmp84dcd92l.cbc/total.s3erlei.hcp72.archivas.com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100'.split('/tmp84dcd92l.cbc/')
                    # base = ['./_hcpcbc.dir', 'total.s3erlei.hcp72.archivas.com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100']

                    p = base[1].split('.')
                    # p = ['total', 's3erlei', 'hcp72', 'archivas', 'com', '2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100']
                    copytgt = join(
                            hcpcbc.Ivars.conf['3 stores']['2 local']['2 path'],
                            p[2], p[1], '__raw', p[0], p[-1]) + '.csv'

                    makedirs(dirname(copytgt), exist_ok=True)
                    self.logger.debug('copy-ing from {} to {}'.format(copysrc,
                                                                      copytgt))
                    copyfile(copysrc, copytgt)
                except Exception as e:
                    self.logger.error('\tcopy of {} failed\n\t\thint: {}'
                                      .format(copysrc, e))

        # self.cookedfiles = [
        #     ',/tmp5td_xq7f.cbc/hcp73/s3/72-created-01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/73-created-01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/test01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/__tenant/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/72-created-01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/73-created-01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/test01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/__tenant/hour/2015-12-20T14:00:00+0100.csv']
        for copysrc in self.cookedfiles:
            p = Path(copysrc).parts[-5:]
            # p = ('hcp72', 'swifty', 'newbucket', 'total', '2015-10-27T14:22:44+0100.csv'

            copytgt = join(hcpcbc.Ivars.conf['3 stores']['2 local']['2 path'],
                           p[-5], p[-4], p[-3], p[-2], p[-1]) + '.csv'
            self.logger.debug('\t\t{} --> {}'.format(copysrc, copytgt))
            try:
                makedirs(dirname(copytgt), exist_ok=True)
                copyfile(copysrc, copytgt)
            except Exception as e:
                self.logger.error('\tcopy of {} failed\n\t\thint: {}'
                                  .format(copytgt, e))

    def transfercompliant(self):
        '''
        Transfer the generated files to the compliant store.
        '''
        self.logger.info('\ttranfering reports to compliant store')

        adr = urlparse(hcpcbc.Ivars.conf['3 stores']['3 compliant']['2 path'])
        if not adr.netloc:
            raise hcpcbc.HcpcbcError("['3 stores']['3 compliant']['2 path'] "
                                     "lacks netloc")
        if not adr.scheme:
            raise hcpcbc.HcpcbcError("['3 stores']['3 compliant']['2 path'] "
                                     "lacks scheme")
        if adr.scheme == 'https':
            port = hcpsdk.P_HTTPS
        elif adr.scheme == 'http':
            port = hcpsdk.P_HTTP
        else:
            raise hcpcbc.HcpcbcError("['3 stores']['3 compliant']['2 path'] "
                                     "invalid scheme")

        auth = hcpsdk.NativeAuthorization(
                hcpcbc.Ivars.conf['3 stores']['3 compliant']['3 user'],
                hcpcbc.Ivars.conf['3 stores']['3 compliant']['4 password'])
        target = hcpsdk.Target(adr.netloc, auth, port=port)
        con = hcpsdk.Connection(target)


        if hcpcbc.Ivars.conf['3 stores']['3 compliant']['9 store raw']:
            # self.rawfiles = [
            #     './_hcpcbc.dir/tmp84dcd92l.cbc/total.s3erlei.hcp72.archivas.com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100',
            #    ]
            for copysrc in self.rawfiles:
                try:
                    base = copysrc.split(self.tempstore.name + '/')
                    # copyysrc = './_hcpcbc.dir/tmp84dcd92l.cbc/total.s3erlei.hcp72.archivas.com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100'.split('/tmp84dcd92l.cbc/')
                    # base = ['./_hcpcbc.dir', 'total.s3erlei.hcp72.archivas.com.2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100']

                    p = base[1].split('.')
                    # p = ['total', 's3erlei', 'hcp72', 'archivas', 'com', '2015-10-29T09:05:33+0100_2015-12-29T21:55:55+0100']
                    tgtpath = '/'.join([adr.path, p[2], p[1], '__raw', p[0],
                                        p[-1]]) + '.csv'

                    self.logger.debug('\t\t{} --> {}'.format(copysrc,
                                                               tgtpath))

                    with open(copysrc, 'rb') as shdl:
                        con.PUT(tgtpath, body=shdl,
                                params={'retention':
                                            hcpcbc.Ivars.conf['3 stores'][
                                                '3 compliant']['5 retention']})
                except Exception as e:
                    self.logger.error('\tingest of {} failed\n\t\thint: {}'
                                      .format(tgtpath, e))
                else:
                    status = con.response_status
                    reason = con.response_reason
                    if status not in [201, 409]:
                        self.logger.warning('ingest failed for {} ({}-{})'
                                            .format(self.fqdn,
                                                    status, reason))

        # self.cookedfiles = [
        #     ',/tmp5td_xq7f.cbc/hcp73/s3/72-created-01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/73-created-01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/test01/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/__tenant/day/2015-12-20T00:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/72-created-01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/73-created-01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/test01/hour/2015-12-20T14:00:00+0100.csv',
        #     './tmp5td_xq7f.cbc/hcp73/s3/__tenant/hour/2015-12-20T14:00:00+0100.csv'.
        for copysrc in self.cookedfiles:
            p = Path(copysrc).parts[-5:]
            # p = ('hcp72', 'swifty', 'newbucket', 'total', '2015-10-27T14:22:44+0100.csv'
            tgtpath = '/'.join(
                    [adr.path, p[-5], p[-4], p[-3], p[-2], p[-1]]) + '.csv'

            self.logger.debug('\t\t{} --> {}'.format(copysrc, tgtpath))
            try:
                with open(copysrc, 'rb') as shdl:
                    con.PUT(tgtpath, body=shdl,
                            params={'retention':
                                        hcpcbc.Ivars.conf['3 stores'][
                                            '3 compliant']['5 retention']})
            except Exception as e:
                self.logger.error('\tcopy of {} failed\n\t\thint: {}'
                                  .format(tgtpath, e))
            else:
                status = con.response_status
                reason = con.response_reason
                if status not in [201, 409]:
                    self.logger.warning('ingest failed for {} ({}-{})'
                                        .format(self.fqdn,
                                                status, reason))

        con.close()

    def close(self):
        """
        Close the session with HCP
        """
        self.cb.close()
