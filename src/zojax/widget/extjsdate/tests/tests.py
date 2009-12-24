##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" zojax.widget.extjsdate tests

$Id$
"""
import os, unittest, doctest
from zope import interface, component
from zope.app.rotterdam import Rotterdam
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite
from zojax.layoutform.interfaces import ILayoutFormLayer


zojaxExtJSDateLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxExtJSDateLayer', allow_teardown=True)


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    testbrowser = FunctionalDocFileSuite(
        "testbrowser.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    testbrowser.layer = zojaxExtJSDateLayer

    return unittest.TestSuite((testbrowser, ))
