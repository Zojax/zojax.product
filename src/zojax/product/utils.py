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
from zope import interface, event, component
from zope.component import queryUtility
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.proxy import removeSecurityProxy

from zope.app.component.hooks import getSite
from zope.app.component.site import SiteManagementFolder
from zope.app.component.interfaces import ISite

from zojax.product.interfaces import _, IProduct


def registerUtility(id, factory, ifaces, container='system'):
    site = getSite()
    if not ISite.providedBy(site):
        raise RuntimeError(_("Can't create utility."))

    sm = component.getSiteManager()

    if isinstance(container, basestring):
        if container:
            if container not in sm:
                folder = SiteManagementFolder()
                event.notify(ObjectCreatedEvent(folder))
                sm[container] = folder

            container = sm[container]
        else:
            container = sm
    elif container is None:
        container = sm

    if id not in container:
        if callable(factory):
            utility = factory()
        else:
            utility = component.createObject(factory)

        event.notify(ObjectCreatedEvent(utility))
        removeSecurityProxy(container)[id] = utility

        for iface, name in ifaces:
            sm.registerUtility(utility, iface, name)

    return container[id]


def unregisterUtility(id, ifaces, container='system'):
    site = getSite()
    sm = component.getSiteManager()

    if container not in sm:
        return

    container = sm[container]

    if id in container:
        utility = container[id]

        for iface, name in ifaces:
            sm.unregisterUtility(utility, iface, name)

        del container[id]


class ProductTest(object):

    def __init__(self, product):
        self.product = product

    def __call__(self, *args, **kw):
        product = queryUtility(IProduct, self.product)
        if product is not None:
            return product.__installed__

        return False
