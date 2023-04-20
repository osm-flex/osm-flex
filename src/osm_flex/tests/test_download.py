import unittest
from osm_flex.download import _create_gf_download_url, get_country_geofabrik, get_region_geofabrik, get_planet_file

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
