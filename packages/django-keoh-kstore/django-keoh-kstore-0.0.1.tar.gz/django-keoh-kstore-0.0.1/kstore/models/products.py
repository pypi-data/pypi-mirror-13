from django.db import models

from .suppliers import Supplier
from .manufacturers import Manufacturer

from kstore.managers.products import ProductManager

class Product(models.Model):

    supplier = models.ForeignKey(Supplier, verbose_name="Supplier", blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, verbose_name="Manufacturer", blank=True, null=True)

    name = models.CharField(u'Product Name',max_length=255)
    description = models.TextField(u'Product description', blank=True, null=True)
    description_short = models.TextField(u'Short description', blank=True, null=True)

    ean13 = models.CharField(u'Codigo de barras',max_length=13, blank=True, null=True)

    width = models.DecimalField(u'Width in cm', max_digits=20, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(u'Height in cm', max_digits=20, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField(u'Depth in cm', max_digits=20, decimal_places=2, blank=True, null=True)

    weight = models.DecimalField(u'Weight in kg',max_digits=20, decimal_places=2, blank=True, null=True)

    quantity = models.PositiveSmallIntegerField(u'Quantity', default=0)

    price = models.DecimalField(u'Price in euros',max_digits=20, decimal_places=2)
    cost_price = models.DecimalField(u'Cost price in euros',max_digits=20, decimal_places=2)

    taxes = models.DecimalField(u'Taxes',max_digits=20, decimal_places=2)

    out_of_stock = models.BooleanField(u'Out of Stock', default=True)

    objects = ProductManager()

    def pure_profit_margin(self):
        return self.price - self.cost_price

    def profit_over_sale(self):
        return round((self.pure_profit_margin()/self.price)*100, 3)

    def profit_over_cost(self):
        return round((self.pure_profit_margin()/self.cost_price)*100,3)

    def abailability(self):
        if self.quantity > 0:
            return True
        else:
            return False

    def stockage_value(self):
        return self.cost_price * self.quantity

    def volume(self):
        vol = self.width * self.height * self.depth
        return vol

    # Admin only methods

    def profit_over_sale_admin(self):
        txt = str(self.profit_over_sale())+' %'
        return txt

    def profit_over_cost_admin(self):
        txt = str(self.profit_over_cost())+' %'
        return txt

    profit_over_sale_admin.short_description = 'Profit over sales'
    profit_over_cost_admin.short_description = 'Profit over cost'

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'ks_product'
