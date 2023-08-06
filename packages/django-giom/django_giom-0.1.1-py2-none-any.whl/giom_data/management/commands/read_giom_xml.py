

from django.core.management.base import BaseCommand, CommandError
from giom_data. GiomDataReader import GiomDataReader
from django.conf import settings


class Command(BaseCommand):
    help = 'Read data from GIOM meteo station in XML'

    def handle(self, *args, **options):
        gdr = GiomDataReader(settings.GIOM_URL)
        print gdr.read_data_xml()

