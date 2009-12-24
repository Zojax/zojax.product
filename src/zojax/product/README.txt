=================
Products (Add-on)
=================

Products system based on z3c.baseregistry package. This package
simplify creating and managing registries.

Loading zcml configuration

  >>> import zojax.product
  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.string("""
  ... <configure xmlns:zojax="http://namespaces.zope.org/zojax"
  ...    xmlns="http://namespaces.zope.org/zope" i18n_domain="zojax">
  ...    <include package="zojax.controlpanel" file="meta.zcml" />
  ...    <include package="zojax.product" file="meta.zcml" />
  ...    <include package="zope.security" file="meta.zcml" />
  ...    <include package="z3c.baseregistry" file="meta.zcml" />
  ...    
  ...    <permission
  ...      id="zojax.ManageProducts"
  ...      title="Manage products" />
  ...      
  ...    <zojax:configlet
  ...      name="product"
  ...      schema="zojax.product.interfaces.IProductInstaller"
  ...      title="Products management"
  ...      description="This is the Add-on Products install section."
  ...      class="zojax.product.installer.ProductsInstaller"
  ...      permission="zojax.ManageProducts" />
  ...
  ... </configure>""")

  >>> from zope import component, interface
  >>> from zojax.controlpanel.interfaces import IConfiglet

  >>> installer = component.getUtility(IConfiglet, 'product')
  >>> installer.keys()
  ()

  >>> installer.isAvailable()
  False

  >>> from zope import schema, interface

  >>> class IMyProduct(interface.Interface):
  ...     """ Basic product """
  ...
  ...     email = schema.TextLine(
  ...         title=u"E-mail Address",
  ...         description=u"E-mail Address used to send notifications")

  >>> context = xmlconfig.string('''
  ... <configure
  ...    xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ... 
  ...   <zojax:product
  ...     name="my-product"
  ...     title="My product"
  ...     configurable="true"
  ...     schema="zojax.product.README.IMyProduct" />
  ...
  ... </configure>''', context)

After registration we can get product declaration by it's schema.

  >>> from zojax.product.interfaces import IProduct

  >>> product = component.getUtility(IMyProduct)
  >>> product
  <zojax.controlpanel.configlettype.Configlet<product.my-product> ...>

  >>> product.__title__
  u'My product'

  >>> IMyProduct.providedBy(product)
  True

Or we can get product by it's name

  >>> component.getUtility(IProduct, 'my-product') is product
  True

But product is also is configlet, configlet name is 'product.' prefix
and product name

  >>> configlet = component.getUtility(IConfiglet, 'product.my-product')
  >>> configlet
  <zojax.controlpanel.configlettype.Configlet<product.my-product> ...>

  >>> configlet is product
  True


Product manipulation
--------------------

Instalation status

  >>> product.isInstalled()
  False

or

  >>> product.__installed__
  False

Instalation

  >>> product.install()
  >>> product.__installed__
  True

  >>> product.install()
  Traceback (most recent call last):
  ...
  ProductAlreadyInstalledError: Product already installed.
  

Updateing product

  >>> product.update()

uninstall

  >>> product.uninstall()
  >>> product.__installed__
  False

we can't uninstall or update not installed product

  >>> product.uninstall()
  Traceback (most recent call last):
  ...
  ProductNotInstalledError: Product is not installed.

  >>> product.update()
  Traceback (most recent call last):
  ...
  ProductNotInstalledError: Product is not installed.


Product dependencies
--------------------
Product can depends on other products.

  >>> class IMyProduct2(interface.Interface):
  ...     """ Product 2 """
  ...
  ...     email = schema.TextLine(
  ...         title=u"E-mail Address",
  ...         description=u"E-mail Address used to send notifications")

  >>> context = xmlconfig.string('''
  ... <configure
  ...    xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ... 
  ...   <zojax:product
  ...     name="my-product2"
  ...     title="My product2"
  ...     require="my-product"
  ...     schema="zojax.product.README.IMyProduct2" />
  ...
  ... </configure>''', context)

'my-product2' is depends on 'my-product'

  >>> product = component.getUtility(IMyProduct)
  >>> product.__installed__
  False

  >>> product2 = component.getUtility(IMyProduct2)
  >>> product2.__require__
  [u'my-product']

Let's install my-product2

  >>> product2.install()

Now both products are installed

  >>> product.__installed__
  True

  >>> product2.__installed__
  True

But on uninstall required products stay intalled

  >>> product2.uninstall()
  
  >>> product.__installed__
  True

  >>> product.uninstall()


Component registry
------------------

When we register product, system automaticly creates component registry

  >>> registry = zojax.product.registries['my-product']

  >>> print registry
  Product: My product

  >>> repr(registry)
  '<Product: My product>'

  >>> component.interfaces.IComponents.providedBy(registry)
  True

When we install product, product's component registry automaticly
added to current site manager bases.

  >>> component.getSiteManager().__bases__
  (<BaseGlobalComponents base>,)

  >>> product.install()

  >>> component.getSiteManager().__bases__
  (<Product: My product>, <BaseGlobalComponents base>)

  >>> product.uninstall()
  >>> component.getSiteManager().__bases__
  (<BaseGlobalComponents base>,)

With z3c.baseregistry it's possible to use <registerIn />
directive. For example:

<registerIn registry="zojax.product.my-product>
  ... various declarations
</registerIn>


Product configlet
-----------------

  >>> installer = component.getUtility(IConfiglet, 'product')
  >>> installer.keys()
  (u'my-product', u'my-product2')

  >>> installer.isAvailable()
  True

  >>> installer['my-product'] is product
  True

  >>> product.isAvailable()
  False

  >>> product.install()
  >>> product.isAvailable()
  True
