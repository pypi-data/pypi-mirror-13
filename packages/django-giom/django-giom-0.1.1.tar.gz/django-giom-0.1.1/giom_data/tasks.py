

from celery import shared_task
from logging import getLogger
from giom_data.GiomDataReader import GiomDataReader
from django.conf import settings
from statsd.defaults.django import statsd
from django.core.cache import cache
from time import time

logger = getLogger("django.giom")
logger_fd = getLogger("fluend.giom")


@shared_task
def refresh_giom_data():
    ds = GiomDataReader(settings.GIOM_URL)
    ds.read()

    d = {}
    m = []
    tmp_dic = ds.dict()
    for k in tmp_dic:
        d["giom.%s" % k] = tmp_dic[k]
        m.append("%s: %s" % (k, tmp_dic[k]))
        statsd.gauge("meteo.giom.%s" % (k), tmp_dic[k])

    logger_fd.info(d)
    logger.debug("GIOM data: %s" % (",".join(m)))
    d = ds.dict()
    d['timestamp'] = time()
    cache.set("meteo-giom", d)
