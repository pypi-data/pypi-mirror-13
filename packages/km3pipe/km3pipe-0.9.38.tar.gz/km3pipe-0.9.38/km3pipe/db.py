# coding=utf-8
# Filename: db.py
# pylint: disable=locally-disabled
"""
Database utilities.

"""
from __future__ import division, absolute_import, print_function

from datetime import datetime
import ssl
import sys
import json
import re

import pandas as pd

from km3pipe.tools import Timer
from km3pipe.config import Config
from km3pipe.logger import logging

if sys.version_info.major > 2:
    from urllib.parse import urlencode, unquote
    from urllib.request import (Request, build_opener,
                                HTTPCookieProcessor, HTTPHandler)
    from io import StringIO
    from http.cookiejar import CookieJar
else:
    from urllib import urlencode, unquote
    from urllib2 import (Request, build_opener,
                         HTTPCookieProcessor, HTTPHandler)
    from StringIO import StringIO
    from cookielib import CookieJar

__author__ = 'tamasgal'

log = logging.getLogger(__name__)  # pylint: disable=C0103


# Ignore invalid certificate error
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    log.warn("Your SSL support is outdate. "
             "Please update your Python installation!")

LOGIN_URL = 'https://km3netdbweb.in2p3.fr/home.htm'
BASE_URL = 'https://km3netdbweb.in2p3.fr'


class DBManager(object):
    """A wrapper for the KM3NeT Web DB"""
    def __init__(self, username=None, password=None):
        "Create database connection"
        self.cookies = []
        self._parameters = None
        self._doms = None
        self._detectors = None
        self._opener = None
        if username is None:
            config = Config()
            username, password = config.db_credentials
        self.login(username, password)

    def datalog(self, parameter, run, maxrun=None, detid='D_ARCA001'):
        "Retrieve datalogs for given parameter, run(s) and detector"
        parameter = parameter.lower()
        if maxrun is None:
            maxrun = run
        with Timer('Database lookup'):
            return self._datalog(parameter, run, maxrun, detid)

    def _datalog(self, parameter, run, maxrun, detid):
        "Extract data from database"
        values = {'parameter_name': parameter,
                  'minrun': run,
                  'maxrun': maxrun,
                  'detid': detid,
                  }
        data = urlencode(values)
        content = self._get_content('streamds/datalognumbers.txt?' + data)
        if content.startswith('ERROR'):
            log.error(content)
            return None
        try:
            dataframe = pd.read_csv(StringIO(content), sep="\t")
        except ValueError:
            log.warning("Empty dataset")  # ...probably. Waiting for more info
            return pd.DataFrame()
        else:
            def convert_data(timestamp):
                return datetime.fromtimestamp(float(timestamp) / 1e3)
            dataframe['DATETIME'] = dataframe['UNIXTIME'].apply(convert_data)
            convert_unit = self.parameters.get_converter(parameter)
            dataframe['VALUE'] = dataframe['DATA_VALUE'].apply(convert_unit)
            dataframe.unit = self.parameters.unit(parameter)
            return dataframe

    def run_table(self, detid='D_ARCA001'):
        url = 'streamds/runs.txt?detid={0}'.format(detid)
        content = self._get_content(url)
        try:
            dataframe = pd.read_csv(StringIO(content), sep="\t")
        except ValueError:
            log.warning("Empty dataset")
            return None
        else:
            def convert_data(timestamp):
                return datetime.fromtimestamp(float(timestamp) / 1e3)
            try:
                converted = dataframe['UNIXSTARTTIME'].apply(convert_data)
                dataframe['DATETIME'] = converted
            except KeyError:
                log.warn("Could not add DATETIME column")
            return dataframe

    @property
    def detectors(self):
        if not self._detectors:
            self._detectors = self._get_detectors()
        return self._detectors

    def _get_detectors(self):
        content = self._get_content('streamds/detectors.txt')
        try:
            dataframe = pd.read_csv(StringIO(content), sep="\t")
        except ValueError:
            log.warning("Empty dataset")
            return pd.DataFrame()
        else:
            return dataframe

    @property
    def parameters(self):
        "Return the parameters container for quick access to their details"
        if self._parameters is None:
            self._load_parameters()
        return self._parameters

    def _load_parameters(self):
        "Retrieve a list of available parameters from the database"
        parameters = self._get_json('allparam/s')
        data = {}
        for parameter in parameters:  # There is a case-chaos in the DB
            data[parameter['Name'].lower()] = parameter
        self._parameters = ParametersContainer(data)

    @property
    def doms(self):
        if self._doms is None:
            self._load_doms()
        return self._doms

    def _load_doms(self):
        "Retrieve DOM information from the database"
        doms = self._get_json('domclbupiid/s')
        self._doms = DOMContainer(doms)

    def _get_json(self, url):
        "Get JSON-type content"
        content = self._get_content('jsonds/' + url)
        json_content = json.loads(content.decode())
        if json_content['Comment']:
            log.warn(json_content['Comment'])
        if json_content['Result'] != 'OK':
            raise ValueError('Error while retrieving the parameter list.')
        return json_content['Data']

    def _get_content(self, url):
        "Get HTML content"
        target_url = BASE_URL + '/' + unquote(url)
        f = self.opener.open(target_url.encode('utf-8'))
        content = f.read()
        return content.decode('utf-8')

    @property
    def opener(self):
        "A reusable connection manager"
        if self._opener is None:
            opener = build_opener()
            for cookie in self.cookies:
                cookie_str = cookie.name + '=' + cookie.value
                opener.addheaders.append(('Cookie', cookie_str))
            self._opener = opener
        return self._opener

    def login(self, username, password):
        "Login to the databse and store cookies for upcoming requests."
        cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cj), HTTPHandler())
        values = {'usr': username, 'pwd': password}
        data = urlencode(values)
        req = Request(LOGIN_URL, data.encode('utf-8'))
        f = opener.open(req)
        html = f.read()
        if 'Bad username or password' in str(html):
            log.error("Bad username or password!")
        self.cookies = cj


class ParametersContainer(object):
    """Provides easy access to parameters"""
    def __init__(self, parameters):
        self._parameters = parameters
        self._converters = {}

    @property
    def names(self):
        "A list of parameter names"
        return self._parameters.keys()

    def get_parameter(self, parameter):
        "Return a dict for given parameter"
        parameter = self._get_parameter_name(parameter)
        return self._parameters[parameter]

    def get_converter(self, parameter):
        """Generate unit conversion function for given parameter"""
        if parameter not in self._converters:
            param = self.get_parameter(parameter)
            try:
                scale = float(param['Scale'])
            except KeyError:
                scale = 1

            def convert(value):
                # easy_scale = float(param['EasyScale'])
                # easy_scale_multiplier = float(param['EasyScaleMultiplier'])
                return value * scale

            return convert

    def unit(self, parameter):
        "Get the unit for given parameter"
        parameter = self._get_parameter_name(parameter).lower()
        return self._parameters[parameter]['Unit']

    def _get_parameter_name(self, parameter):
        if parameter in self.names:
            return parameter
        log.info("Parameter '{0}' not found, trying to find alternative."
                 .format(parameter))
        try:
            # ahrs_g[0] for example should be looked up as ahrs_g
            alternative = re.findall(r'(.*)\[[0-9*]\]', parameter)[0]
            log.info("Found alternative: '{0}'".format(alternative))
            return alternative
        except IndexError:
            raise KeyError("Could not find alternative for '{0}'"
                           .format(parameter))


class DOMContainer(object):
    """Provides easy access to DOM parameters"""
    def __init__(self, doms):
        self._json = doms
        self._ids = []

    def ids(self, det_id):
        """Return a list of DOM IDs for given detector"""
        return [dom['DOMId'] for dom in self._json if dom['DetOID'] == det_id]

    def clbupi2domid(self, clb_upi, det_id):
        """Return DOM ID for given CLB UPI and detector"""
        lookup = [dom['DOMId'] for dom in self._json if
                  dom['DetOID'] == det_id and
                  dom['CLBUPI'] == clb_upi]
        if len(lookup) > 1:
            log.warn("Multiple entries found: {0}".format(lookup) + "\n" +
                     "Return the first one.")
        return lookup[0]
