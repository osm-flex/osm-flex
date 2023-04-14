#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unittests written by ChatGPT
"""

import unittest
from unittest.mock import patch, call
from pathlib import Path
import urllib.request
from osm-flex.download import _create_gf_download_url, get_data_geofabrik, get_data_planet

class TestDownloadFunctions(unittest.TestCase):
    @patch('osm-flex.download.urllib.request.urlretrieve')
    def test_create_gf_download_url_shp(self, mock_urlretrieve):
        expected_url = 'https://download.geofabrik.de/europe/germany-latest-free.shp.zip'
        self.assertEqual(_create_gf_download_url('DEU', 'shp'), expected_url)

    @patch('osm-flex.download.urllib.request.urlretrieve')
    def test_create_gf_download_url_pbf(self, mock_urlretrieve):
        expected_url = 'https://download.geofabrik.de/europe/germany-latest.osm.pbf'
        self.assertEqual(_create_gf_download_url('DEU', 'pbf'), expected_url)

    @patch('osm-flex.download.urllib.request.urlretrieve')
    @patch('osm-flex.download.Path')
    def test_get_data_geofabrik_downloads_new_file(self, mock_path, mock_urlretrieve):
        mock_path.return_value.is_file.return_value = False
        expected_download_url = 'https://download.geofabrik.de/europe/germany-latest-free.shp.zip'
        expected_filepath = Path('/some/path/germany-latest-free.shp.zip')
        get_data_geofabrik('DEU', 'shp', '/some/path')
        mock_path.assert_has_calls([call('/some/path/germany-latest-free.shp.zip')])
        mock_urlretrieve.assert_called_once_with(expected_download_url, expected_filepath)

    @patch('osm-flex.download.urllib.request.urlretrieve')
    @patch('osm-flex.download.Path')
    def test_get_data_geofabrik_does_not_download_existing_file(self, mock_path, mock_urlretrieve):
        mock_path.return_value.is_file.return_value = True
        expected_download_url = 'https://download.geofabrik.de/europe/germany-latest-free.shp.zip'
        expected_filepath = Path('/some/path/germany-latest-free.shp.zip')
        get_data_geofabrik('DEU', 'shp', '/some/path')
        mock_path.assert_has_calls([call('/some/path/germany-latest-free.shp.zip')])
        mock_urlretrieve.assert_not_called()

    @patch('osm-flex.download.urllib.request.urlretrieve')
    @patch('osm-flex.download.Path')
    def test_get_data_planet_downloads_new_file(self, mock_path, mock_urlretrieve):
        mock_path.return_value.is_file.return_value = False
        expected_filepath = Path('/some/path/planet-latest.osm.pbf')
        get_data_planet('/some/path/planet-latest.osm.pbf')
        mock_path.assert_has_calls([call('/some/path/planet-latest.osm.pbf')])
        mock_urlretrieve.assert_called_once_with('https://planet.osm.org/planet-latest.osm.pbf', expected_filepath)

    @patch('osm-flex.download.urllib.request.urlretrieve')
    @patch('osm-flex.download.Path')
    def test_get_data_planet_does_not_download_existing_file(self, mock_path, mock_urlretrieve):
        mock_path.return_value.is_file.return_value = True
        expected_filepath = Path('/some/path/planet-latest.osm.pbf')
        get_data_planet('/some/path/planet-latest.osm.pbf')
        mock_path.assert_has_calls([call('/some/path/planet-latest.osm')])
