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
""" zojax:product directive

$Id$
"""
from zope import schema
from zope.configuration import fields
from zope.component.zcml import utility
from zope.component import globalSiteManager
from zope.component.interfaces import IComponents
from zope.security.checker import CheckerPublic

import zojax.product
from zojax.controlpanel.zcml import IConfigletDirective, ConfigletDirective

from interfaces import IProduct
from product import Product
from registry import ProductRegistry


class IProductDirective(IConfigletDirective):

    configurable = schema.Bool(
        title = u'Configurable',
        default = False,
        required = False)

    require = fields.Tokens(
        title = u'Require',
        value_type = schema.TextLine(),
        required = False)


class ProductDirective(ConfigletDirective):

    def __init__(self, _context, name, schema, title,
                 description='', class_=None, provides=(),
                 permission='zojax.ManageProducts', tests=(),
                 configurable=False, require = ()):

        product_class = Product
        if class_ is None:
            class_ = product_class
        else:
            class_ = (class_, product_class)

        if configurable:
            test = ProductTest()
            tests = (test,) + tuple(tests)
        else:
            tests = (NotConfigurable,)

        # create component registry
        registry = ProductRegistry(name, title)
        zojax.product.registries[name] = registry
        setattr(zojax.product, name, registry)
        utility(_context, IComponents, registry, name=name)

        # register configlet
        productName = name
        name = 'product.' + name

        super(ProductDirective, self).__init__(
            _context, name, schema, title,
            description, class_, provides, permission, tests)

        self._class.__require__ = require
        self._class.__product_name__ = productName

        if configurable:
            test.product = self._configlet

        utility(_context, IProduct, self._configlet, name=productName)

        self.require(_context, permission, interface=(IProduct,))
        self.require(_context, CheckerPublic,
                     attributes=('isInstalled', '__installed__'))


class ProductTest(object):

    def __init__(self, product=None):
        self.product = product

    def __call__(self, *args, **kw):
        return self.product.isInstalled()

def NotConfigurable(configlet):
    return False
