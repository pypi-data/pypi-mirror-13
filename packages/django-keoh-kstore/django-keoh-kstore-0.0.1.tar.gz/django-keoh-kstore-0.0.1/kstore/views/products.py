from django.views.generic import TemplateView

from kstore.helpers.mixins import JerarquiaMixin

from kstore.models import Product

class ProductView(JerarquiaMixin, TemplateView):
    template_name = 'kstore/products/index.html'
    jerarquia = ['Catalogo', 'Productos']

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context["precio_medio"] = Product.objects.precio_medio()
        context["valor_inventario_total"] = Product.objects.valor_inventario_total()
        context["products"] = Product.objects.all()
        return context
