import requests
import wget
import tempfile
import os
import numpy as np
from datetime import datetime
import pickle
import hashlib

BASEURL = 'http://cdaweb.gsfc.nasa.gov/WS/cdasr/1'
HEADERS = {'accept': 'application/json'}

CACHE = False
CACHEDIR = None

def set_cache(cache=False, directory=None):
    global CACHE
    global CACHEDIR
    CACHE = False
    CACHEDIR = None
    if cache and directory is not None:
        directory = os.path.abspath(directory)
        if os.path.isdir(directory):
            CACHE = True
            CACHEDIR = directory

def get_dataviews():
    url = '/'.join([BASEURL, 'dataviews'])
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_observatory_groups(dataview, instrumentType=None):
    url = '/'.join([BASEURL, 'dataviews', dataview, 'observatoryGroups'])
    params = {'instrumentType': instrumentType}
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_instrument_types(dataview, observatory=None, observatoryGroup=None):
    url = '/'.join([BASEURL, 'dataviews', dataview, 'instrumentTypes'])
    params = {
        'observatory': observatory, 
        'observatoryGroup': observatoryGroup
    }
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_instruments(dataview, observatory=None):
    url = '/'.join([BASEURL, 'dataviews', dataview, 'instruments'])
    params = {'observatory': observatory}
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_observatories(dataview, instrument=None, instrumentType=None):
    url = '/'.join([BASEURL, 'dataviews', dataview, 'observatories'])
    params = {'instrument': instrument, 'instrumentType': instrumentType}
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_observatory_groups_and_instruments(dataview, instrumentType=None):
    url = '/'.join([
        BASEURL, 'dataviews', dataview, 
        'observatoryGroupsAndInstruments'
    ])
    params = {'instrumentType': instrumentType}
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_datasets(dataview, observatoryGroup=None, instrumentType=None, 
    observatory=None, instrument=None, startDate=None, stopDate=None, 
        idPattern=None, labelPattern=None, notesPattern=None):
    url = '/'.join([BASEURL, 'dataviews', dataview, 'datasets'])
    params = {
        'observatoryGroup': observatoryGroup, 
        'instrumentType': instrumentType,
        'observatory': observatory, 'instrument': instrument,
        'startDate': (
            startDate.strftime('%Y%m%dT%H%M%SZ') if startDate is not None 
            else None
        ), 
        'stopDate': (
            stopDate.strftime('%Y%m%dT%H%M%SZ') if stopDate is not None 
            else None),
        'idPattern': idPattern, 
        'labelPattern': labelPattern, 
        'notesPattern': notesPattern
    }
    response = requests.get(url, params=params, headers=HEADERS)
    return response.json()

def get_inventory(dataview, dataset):
    url = '/'.join([
        BASEURL, 'dataviews', dataview, 
        'datasets', dataset, 
        'inventory'
    ])
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_variables(dataview, dataset):
    url = '/'.join([
        BASEURL, 'dataviews', dataview, 
        'datasets', dataset, 
        'variables'
    ])
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_data(dataview, dataset, startTime, stopTime, variables, 
        cdf=False, bar=True):
    url = '/'.join([
        BASEURL, 'dataviews', dataview, 
        'datasets', dataset, 
        'data', 
        ','.join([
            startTime.strftime('%Y%m%dT%H%M%SZ'), 
            stopTime.strftime('%Y%m%dT%H%M%SZ')
        ]), 
        ','.join(variables)
    ])
    params = {}
    if cdf:
        params = {'format': 'cdf', 'cdfVersion': 3}
    else:
        params = {'format': 'text'}
    if CACHE:
        md5url = hashlib.md5(
            (url+params['format']).encode('utf-8')
        ).hexdigest()
        cache_path = os.path.join(CACHEDIR, 'cache.pkl')
        if os.path.isfile(cache_path):
            with open(cache_path, 'rb') as f:
                cache = pickle.load(f)
        else:
            cache = {}

        if (md5url in cache and 
            not os.path.isfile(
                os.path.join(CACHEDIR, cache[md5url])
            )):
            cache.pop(md5url, None)

        if md5url not in cache:
            response = requests.get(url, params=params, headers=HEADERS)
            if 'FileDescription' in response.json():
                filename = (
                    response.json()['FileDescription'][0]['Name']
                    .split('/')[-1]
                    .split('#')[0]
                    .split('?')[0]
                )
                if os.path.isfile(os.path.join(CACHEDIR, filename)):
                    cache = {k:v for k, v in cache.items() if v != filename}
                    data_path = os.path.join(CACHEDIR, filename)
                else:
                    data_path = wget.download(
                        response.json()['FileDescription'][0]['Name'], 
                        CACHEDIR, 
                        bar=wget.bar_adaptive if bar else None
                    )
                if bar:
                    print('')
            else:
                raise NoDataError
            cache[md5url] = os.path.basename(data_path)
            with open(cache_path, 'wb') as f:
                pickle.dump(cache, f, protocol=2)
        else:
            data_path = os.path.join(CACHEDIR, cache[md5url])
    else:
        response = requests.get(url, params=params, headers=HEADERS)
        if 'FileDescription' in response.json():
            data_path = wget.download(
                response.json()['FileDescription'][0]['Name'], 
                tempfile.gettempdir(), 
                bar=wget.bar_adaptive if bar else None
            )
            if bar:
                print('')
        else:
            raise NoDataError
    if cdf:
        try:
            from spacepy import pycdf
            data = {
                k: np.array(v) for k, v in pycdf.CDF(data_path).copy().items()
            }
        except ImportError:
            if not CACHE:
                os.remove(data_path)
            print('SpacePy and CDF are required for processing CDF files')
    else:
        try:
            from astropy.io import ascii as ascii_
            rdr = ascii_.get_reader(Reader=ascii_.Basic)
            rdr.header.splitter.delimeter = ' '
            rdr.data.splitter.delimeter = ' '
            rdr.header.start_line = 0
            rdr.data.start_line = 0
            rdr.data.end_line = None
            rdr.header.comment = '#'
            rdr.data.comment = r'[^0-9]'
            rdr.data.splitter.process_line = (
                lambda x: x.strip().replace(' ', '_', 1)
            )
            table = rdr.read(data_path)
            data = dict()
            data[table.colnames[0]] = [
                datetime.strptime(x, '%d-%m-%Y_%H:%M:%S.%f') 
                for x in table.columns[0]
            ]
            for i in range(1, len(table.columns)):
                data[table.colnames[i]] = np.array(table.columns[i])
        except ImportError:
            if not CACHE:
                os.remove(data_path)
            print('AstroPy is required for processing ASCII files')
    return data

class NoDataError(Exception):
    pass
