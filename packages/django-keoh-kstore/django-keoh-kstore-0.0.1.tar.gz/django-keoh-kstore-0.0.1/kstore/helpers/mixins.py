from datetime import date, timedelta, datetime
from kstore.helpers.dates import get_week

class JerarquiaMixin(object):
    jerarquia = ['Home', 'Index']

    def get_context_data(self, **kwargs):
        context = super(JerarquiaMixin, self).get_context_data(**kwargs)
        context["jerarquia"] = self.jerarquia
        return context

class DateRangeMixin(object):
    final_date = date.today()
    d = timedelta(days=365)
    initial_date = final_date - d
    dates = [initial_date, final_date]

    def get_context_data(self, **kwargs):
        context = super(DateRangeMixin, self).get_context_data(**kwargs)
        context["dates"] = self.dates
        return context
