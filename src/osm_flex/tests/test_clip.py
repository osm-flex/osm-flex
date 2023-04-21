#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test clip functions
"""

import unittest
import tempfile
import os
import shapely
from pathlib import Path
from osm_flex.clip import (get_admin1_shapes, get_country_shape, 
                           _simplify_shapelist, _shapely2poly, _build_osmosis_cmd,
                           _build_osmconvert_cmd)
from osm_flex.config import OSMCONVERT_PATH


class TestClip(unittest.TestCase):
    def test_get_admin1_shapes(self):
        # Test for valid country code
        result = get_admin1_shapes("CAN")
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
        self.assertIn("Alberta", result.keys())

        # Test for invalid country code
        with self.assertRaises(LookupError):
            get_admin1_shapes("XYZ")

        # Test for invalid input type
        with self.assertRaises(TypeError):
            get_admin1_shapes(123)

    def test_get_country_shape(self):
        # Test for valid country code
        result = get_country_shape("CAN")
        self.assertIsInstance(result, shapely.geometry.base.BaseGeometry)

        # Test for invalid country code
        with self.assertRaises(LookupError):
            get_country_shape("XYZ")

        # Test for invalid input type
        with self.assertRaises(TypeError):
            get_country_shape(123)

    def test__simplify_shapelist(self):
        # Test for valid input
        geom_list = [shapely.geometry.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        result = _simplify_shapelist(geom_list)
        self.assertEqual(result[0].wkt, 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))')

        # Test too small valid input
        geom_list = [shapely.geometry.Polygon([(0, 0), (0.01, 0), (0.01, 0.01), (0, 0.01)])]
        result = _simplify_shapelist(geom_list)
        self.assertFlase(result) #check if result is empty list

        # Test for invalid input type
        with self.assertRaises(TypeError):
            _simplify_shapelist("invalid_input")

    def test__shapely2poly(self):
        # Test for valid input
        geom_list = [shapely.geometry.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_poly")
            _shapely2poly(geom_list, filename)
            with open(filename+".poly", "r") as f:
                content = f.read()
                self.assertIn("Polygons", content)
                self.assertIn("0", content)
                self.assertIn("0.0     0.0", content)
                self.assertIn("1.0     0.0", content)
                self.assertIn("1.0     1.0", content)
                self.assertIn("0.0     1.0", content)
                self.assertIn("END", content)

        # Test for invalid input type
        with self.assertRaises(ValueError):
            _shapely2poly("invalid_input", "test.poly")

    def test__build_osmosis_cmd(self):
        # Test for bbox input
        shape = [0, 0, 1, 1]
        osmpbf_clip_from = "/path/to/planet.osm.pbf"
        osmpbf_output = "/path/to/extract.osm.pbf"
        result = _build_osmosis_cmd(shape, osmpbf_clip_from, osmpbf_output)
        expected_result = [
            'osmosis',
             '--read-pbf',
             'file=/path/to/planet.osm.pbf',
             '--bounding-box',
             'top=1',
             'left=0',
             'bottom=0',
             'right=1',
             '--write-pbf',
             'file=/path/to/extract.osm.pbf']
        self.assertEqual(result, expected_result)
        
        # Test for .poly file input
        shape = "/path/to/shape.poly"
        osmpbf_clip_from = "/path/to/planet.osm.pbf"
        osmpbf_output = "/path/to/extract.osm.pbf"
        result = _build_osmosis_cmd(shape, osmpbf_clip_from, osmpbf_output)
        expected_result = ['osmosis',
         '--read-pbf',
         'file=/path/to/planet.osm.pbf',
         '--bounding-polygon',
         'file=/path/to/shape.poly',
         '--write-pbf',
         'file=/path/to/extract.osm.pbf']
        self.assertEqual(result, expected_result)
        
    def test__build_osmconvert_cmd(self):
        # Test for valid input
        shape = [0, 0, 1, 1]
        osmpbf_clip_from = "/path/to/planet.osm.pbf"
        osmpbf_output = "/path/to/extract.osm.pbf"
        result = _build_osmconvert_cmd(shape, osmpbf_clip_from, osmpbf_output)
        expected_result = [str(OSMCONVERT_PATH),
         '/path/to/planet.osm.pbf',
         '-b=0,0,1,1',
         '--complete-ways',
         '--complete-multipolygons',
         '-o=/path/to/extract.osm.pbf']
        self.assertEqual(result, expected_result)
        
        # Test for .poly file input
        shape = Path("/path/to/shape.poly")
        osmpbf_clip_from = "/path/to/planet.osm.pbf"
        osmpbf_output = "/path/to/extract.osm.pbf"
        result = _build_osmconvert_cmd(shape, osmpbf_clip_from, osmpbf_output)
        expected_result = [str(OSMCONVERT_PATH),
         '/path/to/planet.osm.pbf',
         '-B=/path/to/shape.poly',
         '--complete-ways',
         '--complete-multipolygons',
         '-o=/path/to/extract.osm.pbf']
        self.assertEqual(result, expected_result)
        


if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestClip)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
