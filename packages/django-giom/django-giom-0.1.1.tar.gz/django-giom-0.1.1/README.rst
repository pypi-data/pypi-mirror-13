=====
Django Giom Meteostation
=====

Read data from GIOM Meteo Station. This is proprietary software used by WebEye.services


Quick start
-----------

1. Add "dust_sensor" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'giom_data',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^giom/', include('giom.urls')),

3. update settings
    - GIOM_URL: giom url to gather data

4. set up loggers
    - for fluentd or td-agent  use handler name fluend.giom
    - for django human readable logger handler use django.giom

5. add celery beat schedule settings

    CELERYBEAT_SCHEDULE = {
        'refresh_giom_data': {
            'task': 'giom.tasks.refresh_giom_data',
            'schedule': timedelta(minutes=1)
        }
    }



6. Run `python manage.py migrate` to create the giom models.

