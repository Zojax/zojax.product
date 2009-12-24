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
import logging, sys
from transaction import abort
from zope.component import getUtility, queryUtility, getUtilitiesFor
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.product.interfaces import _, ProductWarningError

def log_exc(msg=''):
    log = logging.getLogger(u'zojax.product')
    log.log(logging.ERROR, msg, exc_info=sys.exc_info())


class InstallerView(object):

    def getProducts(self):
        context = self.context

        installed = []
        notinstalled = []
        hasUninstallable = False

        for name, product in context.items():
            info = {'name': name,
                    'product': product,
                    'title': product.__title__,
                    'description': product.__description__,
                    'uninstallable': product.isUninstallable()}

            if product.isInstalled():
                info['configlet'] = product.isAvailable()
                installed.append((product.__title__, info))
                if info['uninstallable']:
                    hasUninstallable = True
            else:
                notinstalled.append((product.__title__, info))

        installed.sort()
        installed = [info for t, info in installed]

        notinstalled.sort()
        notinstalled = [info for t, info in notinstalled]

        return {'installed': installed, 'notinstalled': notinstalled,
                'hasUninstallable': hasUninstallable}

    def update(self, *args, **kw):
        request = self.request
        context = self.context

        service = IStatusMessage(request)

        if request.has_key('install'):
            products = request.get('availproducts', ())
            if not products:
                service.add(_('Select one or more products to install.'), 'warning')
            else:
                try:
                    for product_id in products:
                        product = context.get(product_id)
                        product.install()

                    service.add(_('Selected products has been installed.'))
                except ProductWarningError, e:
                    abort()
                    service.add(unicode(e), 'warning')
                except Exception, e:
                    abort()
                    log_exc(str(e))
                    service.add(e, 'error')

        elif request.has_key('update'):
            products = request.get('products', ())
            if not products:
                service.add(_('Select one or more products to update.'), 'warning')
            else:
                try:
                    for product_id in products:
                        product = context.get(product_id)
                        product.update()

                    service.add(_('Selected products has been updated.'))
                except Exception, e:
                    abort()
                    log_exc(str(e))
                    service.add(e, 'error')

        elif request.has_key('uninstall'):
            products = request.get('products', ())
            if not products:
                service.add(_('Select one or more products to uninstall.'), 'warning')
            else:
                try:
                    for product_id in products:
                        product = context.get(product_id)
                        product.uninstall()

                    service.add(_('Selected products has been uninstalled.'))
                except Exception, e:
                    abort()
                    log_exc(str(e))
                    service.add(e, 'error')
