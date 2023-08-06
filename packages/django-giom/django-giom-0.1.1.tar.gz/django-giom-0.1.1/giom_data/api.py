"""

  read data from GIOM

"""

from tastypie.resources import Resource
from django.core.cache import cache
from tastypie import fields
import pytz
import time
from datetime import datetime
from django.utils import timezone
from pretty_times import pretty


class GiomResource(Resource):

    timestamp = fields.IntegerField()
    age = fields.CharField()
    windspeed  = fields.FloatField()
    winddir = fields.FloatField()
    windgust = fields.FloatField()
    pressure = fields.FloatField()
    systemp = fields.FloatField()
    temperature = fields.FloatField()
    baraltitude = fields.FloatField()
    windchill = fields.FloatField()
    relhumidity = fields.FloatField()
    abshumidity = fields.FloatField()
    dewpoint  = fields.FloatField()

    class Meta:
        resource_name = 'giom'

    def dehydrate_timestamp(self, obj):
        return obj.obj["timestamp"]

    def dehydrate_age(self, obj):
        dt_measure = self.dehydrate_timestamp(obj)
        if dt_measure is None:
            return None
        local_tz = pytz.timezone(str(timezone.get_default_timezone()))
        t = time.gmtime(dt_measure)
        dt = datetime(*t[:6], tzinfo=pytz.utc).astimezone(local_tz)
        return pretty.date(dt)

    def dehydrate_windspeed(self, obj):
        if obj.obj["windspeed"] is None:
            return None
        return float(obj.obj["windspeed"])

    def dehydrate_winddir(self, obj):
        if obj.obj["winddir"] is None:
            return None
        return float(obj.obj["winddir"])

    def dehydrate_windgust(self, obj):
        if obj.obj["windgust"] is None:
            return None
        return float(obj.obj["windgust"])

    def dehydrate_pressure(self, obj):
        if obj.obj["pressure"] is None:
            return None
        return float(obj.obj["pressure"])

    def dehydrate_systemp(self, obj):
        if obj.obj["systemp"] is None:
            return None
        return float(obj.obj["systemp"])

    def dehydrate_temperature(self, obj):
        if obj.obj["temperature"] is None:
            return None
        return float(obj.obj["temperature"])

    def dehydrate_baraltitude(self, obj):
        if obj.obj["baraltitude"] is None:
            return None
        return float(obj.obj["baraltitude"])

    def dehydrate_windchill(self, obj):
        if obj.obj["windchill"] is None:
            return None
        return float(obj.obj["windchill"])

    def dehydrate_relhumidity(self, obj):
        if obj.obj["relhumidity"] is None:
            return None
        return float(obj.obj["relhumidity"])

    def dehydrate_abshumidity(self, obj):
        if obj.obj["abshumidity"] is None:
            return None
        return float(obj.obj["abshumidity"])

    def dehydrate_dewpoint(self, obj):
        if obj.obj["dewpoint"] is None:
            return None
        return float(obj.obj["dewpoint"])

    def obj_create(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass

    def obj_get(self, bundle, **kwargs):
        v= self.get_object_list(bundle.request)[0]
        return v

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def apply_filters(self, request, applicable_filters):
        pass

    def get_object_list(self, request):
        pass

    def obj_get_list(self, bundle, **kwargs):
        t = cache.get("meteo-giom", {
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

        results = [{
            'pk': 'now',
            'timestamp': t['timestamp'],
            'windspeed': t['windspeed'],
            'winddir': t['winddir'],
            'windgust': t['windgust'],
            'pressure': t['pressure'],
            'systemp': t['systemp'],
            'temperature': t['temperature'],
            'baraltitude': t['baraltitude'],
            'windchill': t['windchill'],
            'relhumidity': t['relhumidity'],
            'abshumidity': t['abshumidity'],
            'dewpoint': t['dewpoint'],
            },
        ]
        return results

    def obj_update(self, bundle, **kwargs):
        pass

    def obj_delete_list_for_update(self, bundle, **kwargs):
        pass
