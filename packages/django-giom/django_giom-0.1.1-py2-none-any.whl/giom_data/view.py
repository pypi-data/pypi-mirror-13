
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache


class GiomDataView(TemplateView):
    template_name = "giom_data.html"

    def get_context_data(self, **kwargs):
        context = super(GiomDataView, self).get_context_data(**kwargs)

        data = cache.get("meteo-giom", {
            'timestamp': None,
            'windspeed':  None,
            'winddir': None,
            'windgust': None,
            'pressure': None,
            'systemp': None,
            'temperature': None,
            'baraltitude': None,
            'windchill': None,
            'relhumidity': None,
            'abshumidity': None,
            'dewpoint': None,
        })

        for k in data:
            context[k] = data[k]
        return context
