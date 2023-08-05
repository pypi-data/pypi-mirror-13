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
import xlsxwriter
from collections import namedtuple
from . import ChartsError
from . import M_DAY, M_HOUR

logging.getLogger('charts.xlsx').addHandler(logging.NullHandler())

# list of fields provided within chargeback reports
fields = ['objectCount', 'ingestedVolume', 'storageCapacityUsed', 'bytesIn',
          'bytesOut', 'reads', 'writes', 'deletes', 'tieredObjects',
          'tieredBytes', 'metadataOnlyObjects', 'metadataOnlyBytes',
          'deleted', 'valid']

# dict of fields, where the position is the key (0...n), name is value
fn = {n: fields[n] for n in range(len(fields))}
# dict of fields, where the fields name is the key, position is value
ff = {fields[n]: n for n in range(len(fields))}

# Index record holding the starting point (top left cell) of a data series in
# an XlsxWrites worksheet
xlsxidx = namedtuple('xlsxidx', 'row, col')


class Handler():
    """
    A handler class for chart generation
    """

    def __init__(self, outfile, tmpdir, hcpname, tenantname=None, mode=None):
        """
        Prepare for generation of a xlsx workbook holding the data for either
        all Tenant summaries or all Namespaces of a specific Tenant.

        Args:
            outfile:    path/name of the xlxs file to be created
            data:       the data structure created by the prep* function
            tmpdir:     temporary folder for scratch data
            hcpname:    the name of the HCP system the data belongs to
            tenantname: the Tenant's name (or None if the Tenant summeries are to
                        be computed
            mode:       the mode (day or hour)
        """
        self.logger = logging.getLogger(__name__ + 'Handler')
        self.logger.debug('handler created for file "{}"'.format(outfile))

        self.hcpname = hcpname          # the HCP system
        self.tenantname = tenantname    # a Tenant name, if not None
        self.mode = mode                # the mode
        self.charts = []                # created charte

        # setup an index dict to be able to find stuff later again
        # self.idx = {item: xlsxidx(row, col)}
        # pointing to the top left cell of the Tenant's data
        self.idx = {}
        self.row = None                 # used in genxlsx()

        try:
            # Create the workbook and add the data worksheet
            self.workbook = xlsxwriter.Workbook(outfile, {'tmpdir': tmpdir})
            self.ws = self.workbook.add_worksheet('data')
        except Exception as e:
            self.logger.error('handling the xlsx failed somehow\n\thint: '
                                  '{}'.format(e))
            raise ChartsError(e)



    def genxlsx(self, data):
        """
        Generate the worksheet holding the data on which the charts are based.

        Args:
            data:       the data structure created by the prep* function

        Returns:        nothing
        """
        self.logger.debug('generating the data worksheet')

        # Setup some vars used to position ourself on the spreadsheet
        headerrow = 0               # the sum headers per Tenant|Namespace
        subheaderrow = 1            # the field headers
        startrow = 2                # the first data row
        datecol = 0                 # the date column
        startcol = datecol + 1      # the date column
        self.row = startrow         # first data row, points to the next row
        col = startcol              # first data col
        nextcol = 1                 # first col for the next entity (Ten|Ns)

        # write Headers
        if self.tenantname:
            self.ws.write(headerrow, datecol, 'Namespaces:')
        else:
            self.ws.write(headerrow, datecol, 'Tenants:')
        self.ws.write(subheaderrow, datecol, 'Date')

        # write the data
        for ts in sorted(data.keys()):  # timestamps
            if self.mode == M_HOUR:
                self.ws.write(self.row, datecol, ts)  # full timestamp needed
            elif self.mode == M_DAY:
                self.ws.write(self.row, datecol, ts[:10])  # just the date needed
            else:
                raise ChartsError('invalid mode ({})'.format(self.mode))
            for item in data[ts].keys():  # Tenants
                # write the header if Tenant seen first
                if item not in self.idx.keys():
                    self.idx[item] = xlsxidx(self.row, nextcol)
                    nextcol += len(data[ts][item])
                    self.ws.write(headerrow, self.idx[item].col, item)
                    # 'objectCount, ingestedVolume, storageCapacityUsed, '
                    # 'bytesIn, bytesOut, reads, writes, deletes, '
                    # 'tieredObjects, tieredBytes, metadataOnlyObjects, '
                    # 'metadataOnlyBytes, deleted, valid')
                    for c in range(len(data[ts][item])):
                        self.ws.write(subheaderrow, self.idx[item].col + c, fn[c])

                # write the data
                for c in range(len(data[ts][item])):
                    # this is to prepare for calculating KiB, MiB, GiB, TiB etc.
                    if c in [0]:
                        dat = float(data[ts][item][c])
                    elif c in [1, 2]:
                        dat = float(data[ts][item][c])
                    elif c in [3, 4]:
                        dat = float(data[ts][item][c])
                    else:
                        try:
                            dat = float(data[ts][item][c])
                        except ValueError:
                            dat = data[ts][item][c] == 'true' or False

                    # catch and handle cells holding bool values instead of float
                    try:
                        self.ws.write(self.row, self.idx[item].col + c, dat)
                    except ValueError:
                        self.ws.write_boolean(self.row, self.idx[item].col + c,
                                         data[ts][item][c] == 'true')
            self.row += 1

        # close needs to be done outside!
        # workbook.close()


    def gencharts(self, abs=True, log=True, charts=None):
        """
        Generate charts for a given workbook

        Args:
            abs:        create charts with absolute scale
            log:        create charts with log scale
            charts:     a list of functions that generate charts from the data
                        worksheet created in self.genxlsx()
        """
        self.logger.debug('generating the chartsheets')
        if not abs and not log:
            raise ChartsError('need at least one of abs or log')
        scale=[]
        if abs:
            scale.append('linear')
        if log:
            scale.append('log')

        for content in fields:
            # skip irrelevant fields
            if content in ['deleted', 'valid']:
                continue
            for _scale in scale:
                self.charts.append(
                    ch_allcharts(content, self.workbook, self.idx,
                                 self.row - 1, self.mode,
                                 self.hcpname, tenantname=self.tenantname,
                                 scale=_scale))


    def close(self):
        """
        Close the workbook
        """
        self.logger.debug('closing the handler')

        if self.charts:
            self.ws.hide()              # hide the data worksheet
            self.charts[0].activate()   # activate the first chart
        self.workbook.close()


def ch_allcharts(content, workbook, idx, lastrow, mode, hcpname, tenantname=None,
                   data='data', scale='linear', ):
    """
    Create charts

    Args:
        content:    on of the *fields* values
        workbook:   the workbook
        idx:        a dict holding xlsxidx records with the coordinates
                    of the data series per Tenant or Namespace
        lastrow:    the last row used in the data worksheet
        mode:       the mode (day or hour)
        scale:      either 'lin' or 'log'
        hcpname:    the name of the HCP system the data belongs to
        tenantname: the name of the Tenant to work on (if ever)
        data:       the name of the worksheet holding the data

    Returns:        the cs object
    """

    # Setup some vars used to position ourself on the spreadsheet
    startrow = 2                # the first data row
    datecol = 0                 # the date column

    cs = workbook.add_chartsheet('{} ({})'.format(content, scale))
    c1 = workbook.add_chart({'type': 'line'})

    # Or using a list of values instead of category/value formulas:
    #     [sheetname, first_row, first_col, last_row, last_col]
    for tenant in sorted(idx.keys(), reverse=False):
        c1.add_series({'categories': ['data', startrow, datecol,
                                      lastrow, datecol],
                       'values': ['data', startrow,
                                  idx[tenant][1] + ff[content],
                                  lastrow,
                                  idx[tenant][1] + ff[content]],
                       'name': tenant,
                       })

    if tenantname:
        c1.set_title({
                         'name': 'Namespaces of "{}" - {}'.format(
                             '.'.join([tenantname, hcpname]), content),
                         'overlay': False,})
    else:
        c1.set_title({'name': 'Tenants of "{}" - {}'.format(
            hcpname, content), 'overlay': False,})


    c1.set_x_axis({'name': 'Dates',
                   'date_axis': True,
                   'name_font': {'size': 14, 'bold': True},
                   'num_font': {'italic': True},
                   })
    if scale == 'log':
        c1.set_y_axis({'name': '-- logarithmic scale --',
                       'log_base': 10,
                       'display_units_visible': True,
                       'num_format': '#,##0'
                       })
    else:
        c1.set_y_axis({'name': '-- linear scale --',
                       'display_units_visible': True,
                       'num_format': '#,##0'
                       })
    cs.set_chart(c1)
    return cs
