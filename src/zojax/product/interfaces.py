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
""" zojax.product interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.product')


class ProductError(Exception):
    """ base error class for product management """


class ProductNotInstalledError(ProductError):
    """ """


class ProductAlreadyInstalledError(ProductError):
    """ """


class InvalidProduct(ProductError):
    """ """


class ProductWarningError(ProductError):
    """ dependencies error """


class RequiredProductNotFound(ProductError):
    """ """


class IProduct(interface.Interface):
    """ product information """

    __product_name__ = schema.TextLine(
        title = u'Product name',
        required = True)

    __require__ = interface.Attribute(u'Require products.')

    __installed__ = interface.Attribute(u'Is product installed.')

    def install():
        """ install and configure product """

    def uninstall():
        """ uninstall product """

    def update():
        """ update product """

    def isInstalled():
        """ is product installed """

    def isUninstallable():
        """ is product uninstallable """


class IProductInstaller(interface.Interface):
    """ installer for external products """


class IAbstractProductEvent(interface.Interface):
    """ base event interface """

    id = schema.TextLine(
        title = u'Product id',
        required = True)

    product = interface.Attribute('IProduct object')


class IProductInstalledEvent(IAbstractProductEvent):
    """ new product installed """


class IProductUninstalledEvent(IAbstractProductEvent):
    """ product uninstalled """


class IProductUpdatedEvent(IAbstractProductEvent):
    """ product updated """


class AbstractProductEvent(object):

    def __init__(self, id, product):
        self.id = id
        self.product = product


class ProductInstalledEvent(AbstractProductEvent):
    interface.implements(IProductInstalledEvent)


class ProductUninstalledEvent(AbstractProductEvent):
    interface.implements(IProductUninstalledEvent)


class ProductUpdatedEvent(AbstractProductEvent):
    interface.implements(IProductUpdatedEvent)
