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
test simplification functions
"""

import unittest
import geopandas as gpd
import shapely as sh
from osm_flex.simplify import (remove_small_polygons, remove_contained_points,
                               remove_contained_polys, remove_exact_duplicates)
from pandas.testing import assert_frame_equal
from pathlib import Path

PATH_TEST_DATA = Path(__file__).parent / 'data'
OSM_FILE = PATH_TEST_DATA / 'test.osm.pbf'


# Define some shapes
coords1 = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.)) #area=1
coords2 = ((0., 0.), (0., 0.1), (0.1, 0.1), (0.1, 0.), (0., 0.)) #area=0.01
polygon1 = sh.Polygon(coords1)
polygon2 = sh.Polygon(coords2)
point1 = sh.Point(1.0, -1.0)
point2 = sh.Point(.5, .5)
line1 = sh.LineString([[0, 0], [1, 0], [1, 1]])
line2 = sh.LineString([[0.25, 0.25], [0.75, 0.75]])

class TestSimplificationFunctions(unittest.TestCase):
    def test_remove_small_polygons(self):
        """ test function remove_small_polygons() """

        gdf_small_poly = gpd.GeoDataFrame(
            geometry = [
                point1,
                line1,
                polygon1,
                polygon2
            ])

        gdf_no_small_poly = gpd.GeoDataFrame(
            geometry = [
                point1,
                line1,
                polygon1,
            ])

        # get rid of polygon2
        gdf_removed = remove_small_polygons(gdf_small_poly, 0.5)

        assert_frame_equal(gdf_removed, gdf_no_small_poly)

    def test_remove_contained_points(self):
        """ test function remove_contained_points() """

        gdf_pnt_in_poly = gpd.GeoDataFrame(
            geometry = [polygon1, polygon2, point1, point2, line1
            ])

        gdf_check  = gpd.GeoDataFrame(
            geometry = [polygon1, polygon2, point1,line1
            ])

        # get rid of point2
        gdf_simple  = remove_contained_points(gdf_pnt_in_poly)

        assert_frame_equal(gdf_check, gdf_simple)



    def test_remove_contained_polys(self):
        """ test function remove_contained_polys() """

        gdf_poly_in_poly = gpd.GeoDataFrame(
            geometry = [polygon1, polygon2, point1, point2, line1, line2
            ])

        gdf_check  = gpd.GeoDataFrame(
            geometry = [polygon1, point1, point2, line1, line2
            ])

        # get rid of polygon2
        gdf_simple = remove_contained_polys(gdf_poly_in_poly)

        assert_frame_equal(gdf_check, gdf_simple)



    def test_remove_exact_duplicates(self):
        """ test function remove_exact_duplicates() """

        gdf_dupl = gpd.GeoDataFrame(
            geometry = [polygon1, polygon1, point1, point1, line1, line1
            ])

        # get rid of polygon1, point1, line1
        gdf_simple = remove_exact_duplicates(gdf_dupl)

        gdf_check  = gpd.GeoDataFrame(
            geometry = [polygon1, point1, line1
            ])

        assert_frame_equal(gdf_check, gdf_simple)


if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestSimplificationFunctions)
    unittest.TextTestRunner(verbosity=2).run(TESTS)