 
import unittest
from ai import cdas
import json
from datetime import datetime
import socket
import shutil
import os

class TestDataviews(unittest.TestCase):
    def testGeneric(self):
        dataviews = cdas.get_dataviews()
        self.assertTrue(isinstance(dataviews, dict), 
            'output is not a dictionary')

class TestObservatoryGroups(unittest.TestCase):
    def testGeneric(self):
        observatoryGroups = cdas.get_observatory_groups('istp_public')
        self.assertTrue(isinstance(observatoryGroups, dict))

    def testByInstrumentType(self):
        observatoryGroups = cdas.get_observatory_groups('istp_public', instrumentType='Plasma and Solar Wind')
        self.assertTrue(isinstance(observatoryGroups, dict))

class TestInstrumentTypes(unittest.TestCase):
    def testGeneric(self):
        instrumentTypes = cdas.get_instrument_types('istp_public')
        self.assertTrue(isinstance(instrumentTypes, dict))

    def testByObservatory(self):
        instrumentTypes = cdas.get_instrument_types('istp_public', observatory='Ahead')
        self.assertTrue(isinstance(instrumentTypes, dict))

    def testByObservatoryGroup(self):
        instrumentTypes = cdas.get_instrument_types('istp_public', observatoryGroup='STEREO')
        self.assertTrue(isinstance(instrumentTypes, dict))

    def testByObservatoryAndGroup(self):
        instrumentTypes = cdas.get_instrument_types('istp_public', observatory='Ahead', observatoryGroup='STEREO')
        self.assertTrue(isinstance(instrumentTypes, dict))

class TestInstruments(unittest.TestCase):
    def testGeneric(self):
        instruments = cdas.get_instruments('istp_public')
        self.assertTrue(isinstance(instruments, dict))

    def testByObservatory(self):
        instruments = cdas.get_instruments('istp_public', observatory='Ahead')
        self.assertTrue(isinstance(instruments, dict))

class TestObservatories(unittest.TestCase):
    def testGeneric(self):
        observatories = cdas.get_observatories('istp_public')
        self.assertTrue(isinstance(observatories, dict))

    def testByInstrument(self):
        observatories = cdas.get_observatories('istp_public', instrument='IMPACT_MAG')
        self.assertTrue(isinstance(observatories, dict))        

    def testByInstrumentType(self):
        observatories = cdas.get_observatories('istp_public', instrumentType='Plasma and Solar Wind')
        self.assertTrue(isinstance(observatories, dict))

    def testByInstrumentAndType(self):
        observatories = cdas.get_observatories('istp_public', instrument='IMPACT_MAG', instrumentType='Plasma and Solar Wind')
        self.assertTrue(isinstance(observatories, dict))

class TestObservatoryGroupsAndInstruments(unittest.TestCase):
    def testGeneric(self):
        observatoryGroupsAndInstruments = cdas.get_observatory_groups_and_instruments('istp_public')
        self.assertTrue(isinstance(observatoryGroupsAndInstruments, dict))

    def testByInstrumentType(self):
        observatoryGroupsAndInstruments = cdas.get_observatory_groups_and_instruments('istp_public', instrumentType='Plasma and Solar Wind')
        self.assertTrue(isinstance(observatoryGroupsAndInstruments, dict))

class TestDatasets(unittest.TestCase):
    def testGeneric(self):
        datasets = cdas.get_datasets('istp_public')
        self.assertTrue(isinstance(datasets, dict))

    def testByObservatoryAndInstrument(self):
        datasets = cdas.get_datasets('istp_public', observatoryGroup='STEREO', instrumentType='Plasma and Solar Wind',
            observatory='Ahead', instrument='IMPACT_MAG')
        self.assertTrue(isinstance(datasets, dict))

    def testByDates(self):
        datasets = cdas.get_datasets('istp_public', observatoryGroup='STEREO', instrumentType='Plasma and Solar Wind',
            observatory='Ahead', instrument='IMPACT_MAG',
            startDate=datetime(2010,1,1), stopDate=datetime(2010,1,2))
        self.assertTrue(isinstance(datasets, dict))

    def testByIdPattern(self):
        datasets = cdas.get_datasets('istp_public', observatoryGroup='STEREO', instrumentType='Plasma and Solar Wind',
            observatory='Ahead', instrument='IMPACT_MAG',
            startDate=datetime(2010,1,1), stopDate=datetime(2010,1,2),
            idPattern='.+1HR$')
        self.assertTrue(isinstance(datasets, dict))

    def testByLabelPattern(self):
        datasets = cdas.get_datasets('istp_public', observatoryGroup='STEREO', instrumentType='Plasma and Solar Wind',
            observatory='Ahead', instrument='IMPACT_MAG',
            startDate=datetime(2010,1,1), stopDate=datetime(2010,1,2),
            labelPattern='.+PLASTIC.+')
        self.assertTrue(isinstance(datasets, dict))

    def testByNotesPattern(self):
        datasets = cdas.get_datasets('istp_public', observatoryGroup='STEREO', instrumentType='Plasma and Solar Wind',
            observatory='Ahead', instrument='IMPACT_MAG',
            startDate=datetime(2010,1,1), stopDate=datetime(2010,1,2),
            notesPattern='.+1DMAX.+')
        self.assertTrue(isinstance(datasets, dict))

class TestInventory(unittest.TestCase):
    def testGeneric(self):
        inventory = cdas.get_inventory('istp_public', 'STA_L2_PLA_1DMAX_1HR')
        self.assertTrue(isinstance(inventory, dict))

class TestVariables(unittest.TestCase):
    def testGeneric(self):
        variables = cdas.get_variables('istp_public', 'STA_L2_PLA_1DMAX_1HR')
        self.assertTrue(isinstance(variables, dict))

class TestData(unittest.TestCase):
    def testCdfFormat(self):
        data = cdas.get_data('istp_public', 'STA_L2_PLA_1DMAX_1HR', 
            datetime(2010,1,1), datetime(2010,1,2), 
            ['proton_bulk_speed_1hr', 'proton_temperature_1hr', 'proton_thermal_speed_1hr'], cdf=True)
        self.assertTrue(isinstance(data, dict))

    def testTextFormat(self):
        data = cdas.get_data('istp_public', 'STA_L2_PLA_1DMAX_1HR', 
            datetime(2010,1,1), datetime(2010,1,2), 
            ['proton_bulk_speed_1hr', 'proton_temperature_1hr', 'proton_thermal_speed_1hr'], cdf=False)
        self.assertTrue(isinstance(data, dict))

    def testCache(self):
        cache_path = '.test_cache'
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        cdas.set_cache(True, cache_path)
        data = cdas.get_data('istp_public', 'STA_L2_PLA_1DMAX_1HR', 
            datetime(2010,1,1), datetime(2010,1,2), 
            ['proton_bulk_speed_1hr', 'proton_temperature_1hr', 'proton_thermal_speed_1hr'], cdf=False)

        def guard(*args, **kwargs):
            raise Exception("I told you not to use the Internet!")
        socket_original = socket.socket

        socket.socket = guard
        data = cdas.get_data('istp_public', 'STA_L2_PLA_1DMAX_1HR', 
            datetime(2010,1,1), datetime(2010,1,2), 
            ['proton_bulk_speed_1hr', 'proton_temperature_1hr', 'proton_thermal_speed_1hr'], cdf=False)
        socket.socket = socket_original

        cdas.set_cache(False)
        shutil.rmtree(cache_path)
        self.assertTrue(isinstance(data, dict))
