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
import tempfile
import os
import shapely
from pathlib import Path
from osm_flex.download import (
    _create_gf_download_url,
    get_country_geofabrik,
    get_region_geofabrik,
    get_planet_file,
)


class TestDownload(unittest.TestCase):

    def test_create_gf_download_url(self):
        with self.assertRaisesRegex(
            KeyError, "The provided iso3 seems not to be available on Geofabrik.de"
        ):
            _create_gf_download_url("XXX", "pbf")

        with self.assertRaisesRegex(NotImplementedError, "Invalid file format 'pdf'"):
            _create_gf_download_url("DEU", "pdf")

        url = _create_gf_download_url("DEU", "pbf")
        self.assertEqual(
            url, "https://download.geofabrik.de/europe/germany-latest.osm.pbf"
        )

        url = _create_gf_download_url("DEU", "shp")
        self.assertEqual(
            url, "https://download.geofabrik.de/europe/germany-latest-free.shp.zip"
        )

        url = _create_gf_download_url("RUS-A", "pbf")
        self.assertEqual(
            url, "https://download.geofabrik.de/asia/russia-latest.osm.pbf"
        )

        url = _create_gf_download_url("RUS-E", "pbf")
        self.assertEqual(
            url, "https://download.geofabrik.de/europe/russia-latest.osm.pbf"
        )

    def test_get_country_geofabrik(self):
        iso3 = "IC"
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "canary-islands-latest.osm.pbf")
            return_value = get_country_geofabrik(iso3, save_path=tmpdir)
            self.assertEqual(return_value, Path(filename))
            self.assertTrue(os.path.exists(filename))

    def test_get_region_geofabrik(self):
        region = "central-america"
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "central-america-latest.osm.pbf")
            return_value = get_region_geofabrik(region, save_path=tmpdir)
            self.assertEqual(return_value, Path(filename))
            self.assertTrue(os.path.exists(filename))

    @unittest.skip("File too large to test download")
    def test_get_planet_file(self):
        self.fail("No test implemented")


if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestDownload)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
