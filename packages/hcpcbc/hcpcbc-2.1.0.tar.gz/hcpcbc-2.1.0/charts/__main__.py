#! /usr/bin/env python3
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

from pprint import pprint

import charts


def main(args=None):
    """The main routine.

    Args:
        args:
    """
    data = charts.prep.prepdata('./_hcpcbc.dir/hcp72',
                                   mode=charts.M_DAY)
    hdl = charts.xlsx.Handler('./_charts/_test_day.xlsx', './_charts', 'hcp72')
    hdl.genxlsx(data)
    hdl.gencharts()
    hdl.close()


    # data = charts.prep.prepdata('./_hcpcbc.dir/hcp72',
    #                                mode=charts.M_DAY)
    # charts.xlsx.genxlsx('./_charts/_test_day.xlsx', data,
    #                                './_charts', 'hcp72')
    #
    # data = charts.prep.prepdata('./_hcpcbc.dir/hcp73/swifttest',
    #                             tenant='swifttest', mode=charts.M_HOUR)
    # charts.xlsx.genxlsx('./_charts/_test_hour.xlsx', data,
    #                                './_charts', 'hcp72', tenantname='swifttest')



if __name__ == '__main__':
    logger = charts.log()
    logger.info('logger initialized')
    main()
