"""
This file is part of OSM-flex.
Copyright (C) 2023 OSM-flex contributors listed in AUTHORS.
OSM-flex is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free
Software Foundation, version 3.
OSM-flex is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.
-----
test extraction functions
"""

import unittest
import geopandas as gpd
from osm_flex.extract import extract, extract_cis, _query_builder
from pathlib import Path

class TestExtractionFunctions(unittest.TestCase):

    def __init__(self):
        self.test_data_path = Path(__file__).parent / 'data' 
        self.osm_file = self.test_data_path / 'test.osm.pbf'

    def test_extract(self):
        gdf = extract(self.osm_file, 'multipolygons', ['name', 'building'], ["building='yes'"])
        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        self.assertEqual(set(gdf.columns), set(['osm_id', 'building', 'name', 'geometry']))

    def test_extract_cis(self):
        pass
    
    def test__queery_builder(self):
        pass

if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestExtractionFunctions)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
