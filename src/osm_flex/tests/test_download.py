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
test download functions
"""

import unittest
from osm_flex.download import (_create_gf_download_url, 
                               get_country_geofabrik, 
                               get_region_geofabrik, 
                               get_planet_file)

class TestDownload(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_gf_download_url(self):
        pass

    def test_get_country_geofabrik(self):
        pass

    def test_get_region_geofabrik(self):
        pass

    def test_get_planet_file(self):
        pass

if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestDownload)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
