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
"""

$Id$
"""
from zope.component import queryUtility
from zope.component.interfaces import IComponents
from zope.component import globalregistry, globalSiteManager

import zojax.product
from zojax.product.interfaces import _


def BC(components, name):
    bc = getattr(zojax.product, name, None)
    if bc is None:
        return broken
    else:
        return bc


class ProductRegistry(globalregistry.BaseGlobalComponents):

    def __init__(self, name, title):
        self.title = title
        self.__name__ = name
        self.__parent__ =  globalSiteManager
        super(ProductRegistry, self).__init__(name)

    def __str__(self):
        return "Product: %s"%self.title

    def __repr__(self):
        return "<Product: %s>"%self.title

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return BC, (self.__parent__, self.__name__)


class BrokenProductRegistry(globalregistry.BaseGlobalComponents):

    def __init__(self):
        self.__parent__ =  globalSiteManager
        super(BrokenProductRegistry, self).__init__('broken')

    def __repr__(self):
        return _("Product: Broken product!!!")


broken = BrokenProductRegistry()
