

from django.core.management.base import BaseCommand, CommandError
from giom_data.tasks import refresh_giom_data


class Command(BaseCommand):
    help = 'Read data from GIOM meteo station and log it'

    def handle(self, *args, **options):
        refresh_giom_data()
