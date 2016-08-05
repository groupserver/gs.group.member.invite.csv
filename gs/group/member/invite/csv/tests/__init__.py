# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 Michael JasonSmith and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from contextlib import contextmanager
import os
from pkg_resources import resource_filename


@contextmanager
def test_data(filename):
    '''A useful function for loading a test file'''
    testname = os.path.join('tests', 'data', filename)
    fullFileName = resource_filename('gs.group.member.invite.csv', testname)
    # --=mpj17=-- Because the file may contain UTF-8 or ISO 8859-1 in
    # full eight-bit glory the file is opened in **binary** mode.
    try:
        retval = open(fullFileName, 'rb')
        yield retval
    finally:
        retval.close()
