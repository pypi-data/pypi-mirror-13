"""

  Read data from GIOM web site, data are in XML format and are stored to statsd and fluentd

  by Vaclav Rak  <me@vena.cz>

"""

import urllib2
from xml.dom import minidom


class GiomDataReader(object):
    _url = None
    _data = {}
    _dom = None

    def __init__(self, url=None):
        self._url = url
        self._data = {}
        self._dom = None

    @property
    def giom_url(self):
        return self._url

    def read_data_xml(self):
        response = urllib2.urlopen(self.giom_url)
        return response.read()

    def parse_xml(self):
        if self._dom is None:
            self._dom = minidom.parseString(self.read_data_xml())

    def read(self):
        if self._data != {}:
            return self

        self.parse_xml()
        dom = self._dom.getElementsByTagName("status")[0]

        for child in dom.childNodes:
            if child.nodeType != 1:
                continue

            k = child.nodeName
            if k == 'devname':
                continue

            v = float(child.childNodes[0].data)

            self._data[k] = v
        return self

    def dict(self):
        return self.read()._data

    def __getitem__(self, k):
        return self.read()._data[k]
    