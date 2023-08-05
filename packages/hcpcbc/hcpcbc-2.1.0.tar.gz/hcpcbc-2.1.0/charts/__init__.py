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

class ChartsError(Exception):
    """
    Raised on generic errors in **hcpcbc.charts**.
    """

    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)

from .init import *
from . import prep
from . import xlsx


#logging.getLogger('charts').addHandler(logging.NullHandler())

def log():
    """
    temporary - Setup logging

    returns:            the logger object
    """

    fh = logging.Formatter('%(asctime)s [%(levelname)-8s] '
                           '%(message)s',
                           '%m/%d %H:%M:%S')

    logger = logging.getLogger()

    sh = logging.StreamHandler()
    sh.setFormatter(fh)
    logger.addHandler(sh)
    logger.setLevel(logging.ERROR)

    l = logging.getLogger(__name__)

    l.info('log() initialized')

    return logger
