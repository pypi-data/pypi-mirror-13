

from django.core.management.base import BaseCommand, CommandError
from giom_data. GiomDataReader import GiomDataReader
from django.conf import settings


class Command(BaseCommand):
    help = 'Read data from GIOM meteo station in CSV'

    def handle(self, *args, **options):
        gdr = GiomDataReader(settings.GIOM_URL)
        d = gdr.dict()
        for k in d:
            print "%s,%s" % (k, d[k])


