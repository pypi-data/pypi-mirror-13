from django.db import models

class ProductManager(models.Manager):
    '''
        Manager para la gestion de los productos
    '''
    def precio_medio(self):
        '''Devuelve el precio medio de todos los productos'''
        suma_precios = 0.0
        productos = self.model.objects.filter(out_of_stock=False)
        if productos.count() == 0:
            return 0
        for prod in productos:
            suma_precios += float(prod.price)

        suma_precios = suma_precios / productos.count()
        return suma_precios

    def valor_inventario_total(self):
        '''Devuelve el valor de todo el inventario'''
        suma_valor = 0.0
        productos = self.model.objects.filter(quantity__gt=0)
        if productos.count() == 0:
            return 0
        for prod in productos:
            suma_valor += float(prod.stockage_value())

        return suma_valor
