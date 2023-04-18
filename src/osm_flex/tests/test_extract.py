#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test extract functions
"""

import unittest
import shutil
from pathlib import Path
import geopandas as gpd
from osm_flex import extract

# TODO: how to test extraction? put a small osm-pbf file into a test/data folder?

class Testextract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.osm_file = 'test.osm.pbf'
        cls.geojson_file = 'test.geojson'
        cls.osm_path = Path(__file__).parent / 'data' / cls.osm_file
        cls.geojson_path = Path(__file__).parent / 'data' / cls.geojson_file
        # create a test output directory
        cls.test_output_dir = Path(__file__).parent / 'output'
        cls.test_output_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # remove the test output directory
        shutil.rmtree(cls.test_output_dir)

    def test_retrieve(self):
        pass

    def test_retrieve_cis(self):
        pass

    def test__query_builder(self):
        pass

if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(Testextract)
    unittest.TextTestRunner(verbosity=2).run(TESTS)                              