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
from osm_flex.simplify import remove_small_polygons
from pathlib import Path

PATH_TEST_DATA = Path(__file__).parent / 'data'
OSM_FILE = PATH_TEST_DATA / 'test.osm.pbf'

class TestSimplificationFunctions(unittest.TestCase):
    def test_remove_small_polygons(self):
        coords1 = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.)) #area=1
        polygon1 = sh.Polygon(coords1)
        coords2 = ((0., 0.), (0., 0.1), (0.1, 0.1), (0.1, 0.), (0., 0.)) #area=0.01
        polygon2 = sh.Polygon(coords2)
        
        gdf_small_poly = gpd.GeoDataFrame(
            geometry = [
                sh.Point(1.0, -1.0),
                sh.LineString([[0, 0], [1, 0], [1, 1]]),
                polygon1,
                polygon2
            ])
        
        gdf_no_small_poly = gpd.GeoDataFrame(
            geometry = [
                sh.Point(1.0, -1.0),
                sh.LineString([[0, 0], [1, 0], [1, 1]]),
                polygon1,
            ])
        
        gdf_removed = remove_small_polygons(gdf_small_poly, 0.5)
        
        self.assertTrue((gdf_removed == gdf_no_small_poly).all().values[0])
        
if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestSimplificationFunctions)
    unittest.TextTestRunner(verbosity=2).run(TESTS)