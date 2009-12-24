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
from BTrees.OOBTree import OOBTree

from zope import interface, event
from zope.component import getSiteManager
from zope.component import getUtility, queryUtility, getUtilitiesFor
from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ILocalSiteManager
from zope.lifecycleevent import ObjectModifiedEvent

from z3c.configurator import configure

import zojax.product
from zojax.controlpanel.configlettype import ConfigletProperty

from zojax.product import interfaces
from zojax.product.interfaces import _, IProduct


class Product(object):
    """ base product class """
    interface.implements(IProduct)

    @property
    def __installed__(self):
        sm = getSiteManager()

        registry = getattr(zojax.product, self.__product_name__)
        return registry in sm.__bases__

    def _checkRequiredInstall(self):
        for productId in self.__require__:
            product = queryUtility(IProduct, productId)
            if product is None:
                raise interfaces.RequiredProductNotFound(
                    _('Required product is not found.'))
            if not product.__installed__:
                product.install()

    def _checkRequiredUpdate(self):
        for productId in self.__require__:
            product = queryUtility(IProduct, productId)
            if product is None:
                raise interfaces.RequiredProductNotFound(
                    _('Required product is not found.'))
            if not product.__installed__:
                product.install()
            else:
                product.update()

    def install(self):
        self._checkRequiredInstall()

        if self.__installed__:
            raise interfaces.ProductAlreadyInstalledError(
                _('Product already installed.'))

        sm = getSiteManager()

        registry = getattr(zojax.product, self.__product_name__)
        sm.__bases__ = (registry,) + sm.__bases__

        if ILocalSiteManager.providedBy(sm):
            for subsm in sm.subs:
                subsm.__bases__ = subsm.__bases__

        event.notify(interfaces.ProductInstalledEvent(self.__product_name__, self))
        event.notify(ObjectModifiedEvent(getSite()))

        self.update()

    def update(self):
        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product is not installed.'))

        configure(self, {})
        event.notify(
            interfaces.ProductUpdatedEvent(self.__product_name__, self))
        event.notify(ObjectModifiedEvent(getSite()))

        self._checkRequiredUpdate()

    def uninstall(self):
        if not self.__installed__:
            raise interfaces.ProductNotInstalledError(
                _('Product is not installed.'))

        sm = getSiteManager()
        registry = getattr(zojax.product, self.__product_name__)

        bases = list(sm.__bases__)
        bases.remove(registry)
        sm.__bases__ = tuple(bases)

        if ILocalSiteManager.providedBy(sm):
            for subsm in sm.subs:
                subsm.__bases__ = subsm.__bases__

        event.notify(
            interfaces.ProductUninstalledEvent(self.__product_name__, self))
        event.notify(ObjectModifiedEvent(getSite()))

    def _checkInstalled(self, sm, registry, seen):
        if sm in seen:
            return False
        seen.add(sm)

        if registry in sm.__bases__:
            return True

        for reg in sm.__bases__:
            if self._checkInstalled(reg, registry, seen):
                return True

        return False

    def isInstalled(self):
        sm = getSiteManager()
        registry = getattr(zojax.product, self.__product_name__)
        seen = set()
        return self._checkInstalled(sm, registry, seen)

    def isUninstallable(self):
        sm = getSiteManager()
        registry = getattr(zojax.product, self.__product_name__)
        return registry in sm.__bases__
