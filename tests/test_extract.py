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
import numpy as np
import shapely as sh
from osm_flex.extract import extract, extract_cis, _query_builder, remove_small_polygons
from pathlib import Path

PATH_TEST_DATA = Path(__file__).parent / 'data'
OSM_FILE = PATH_TEST_DATA / 'test.osm.pbf'

class TestExtractionFunctions(unittest.TestCase):

    def test_extract(self):
        """
        test function extract()
        """
        gdf_mp = extract(OSM_FILE, 'multipolygons',  ['name', 'building'],
                         "building='yes'")
        self.assertIsInstance(gdf_mp, gpd.GeoDataFrame)
        self.assertEqual(set(gdf_mp.columns),
                         set(['osm_id', 'building', 'name', 'geometry']))
        self.assertEqual(np.unique(gdf_mp.geometry.type),
                         np.array(['MultiPolygon']))
        self.assertTrue(len(gdf_mp)==4202)

        gdf_mp2 = extract(OSM_FILE, 'multipolygons',  ['building', 'name'])
        self.assertIsInstance(gdf_mp2, gpd.GeoDataFrame)
        self.assertEqual(set(gdf_mp2.columns),
                         set(['osm_id', 'building', 'name', 'geometry']))
        self.assertEqual(np.unique(gdf_mp2.geometry.type),
                         np.array(['MultiPolygon']))
        self.assertEqual(len(gdf_mp2),5050)
        self.assertFalse(any(elem is None for elem in gdf_mp2.building))


        gdf_line = extract(OSM_FILE, 'lines', ['name', 'highway'],
                           "highway='residential'")
        self.assertIsInstance(gdf_line, gpd.GeoDataFrame)
        self.assertEqual(set(gdf_line.columns),
                         set(['osm_id', 'name', 'highway', 'geometry']))
        self.assertEqual(np.unique(gdf_line.geometry.type),
                         np.array(['LineString']))
        self.assertTrue(len(gdf_line)==1807)

        gdf_line2 = extract(OSM_FILE, 'lines', ['highway','name'], None)
        self.assertIsInstance(gdf_line2, gpd.GeoDataFrame)
        self.assertEqual(set(gdf_line2.columns),
                         set(['osm_id', 'name', 'highway', 'geometry']))
        self.assertEqual(np.unique(gdf_line2.geometry.type),
                         np.array(['LineString']))
        self.assertEqual(len(gdf_line2),3266)
        self.assertFalse(any(elem is None for elem in gdf_line2.highway))

        gdf_line3 = extract(OSM_FILE, 'lines', ['highway'], None)
        self.assertIsInstance(gdf_line3, gpd.GeoDataFrame)
        self.assertEqual(set(gdf_line3.columns),
                         set(['osm_id', 'highway', 'geometry']))
        self.assertEqual(np.unique(gdf_line3.geometry.type),
                         np.array(['LineString']))
        self.assertEqual(len(gdf_line3),3266)
        self.assertFalse(any(elem is None for elem in gdf_line3.highway))


        # TODO: test with invalid geo_type

    def test_extract_cis(self):
        """
        test function extract_cis()
        """
        gdf_schools = extract_cis(OSM_FILE, 'education')
        self.assertTrue(np.any([entry =='college' for entry in gdf_schools.amenity]))
        self.assertTrue(np.any([entry =='school' for entry in gdf_schools.amenity]))
        self.assertTrue(len(gdf_schools)==215)
        self.assertTrue('amenity' in gdf_schools.columns)

        gdf_roads = extract_cis(OSM_FILE, 'road')
        self.assertTrue(np.any([entry =='tertiary' for entry in gdf_roads.highway]))
        self.assertTrue(np.any([entry =='residential' for entry in gdf_roads.highway]))
        self.assertTrue(len(gdf_roads)==2603)
        self.assertTrue('name' in gdf_roads.columns)

        # TODO: test with invalid ci-argument

    def test__query_builder(self):
        """
        test function _query_builder()
        """
        geo_type = 'points'
        constraint_dict = {'osm_keys': ['name', 'highway'],
                           'osm_query' :  "highway='residential'"}
        query = _query_builder(geo_type, constraint_dict)
        self.assertEqual(query,
                         "SELECT osm_id,name,highway FROM points WHERE highway='residential'")

        geo_type = 'points'
        constraint_dict = {'osm_keys': ['name', 'highway'],
                           'osm_query' : None}
        query = _query_builder(geo_type, constraint_dict)
        self.assertEqual(query,
                         'SELECT osm_id,name,highway FROM points WHERE name IS NOT NULL')


    def test_qb_error(self):
        geo_type = 'points'
        constraint_dict2 = {'wrong_key': ['name', 'highway'],
                           'osm_query' :  "highway='residential'"}

        with self.assertRaises(KeyError) as context:
            _query_builder(geo_type, constraint_dict2)
        # TODO: how to check now that raises either keyerror or key error with message
        #self.assertTrue('osm_keys' in context.exception)
        #self.assertTrue(KeyError in context.exception)

        
if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestExtractionFunctions)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
