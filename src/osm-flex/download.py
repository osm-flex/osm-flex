#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
downloading functions
"""

import logging
from pathlib import Path
import urllib.request
from .constants import GEOFABRIK_URL, PLANET_URL, DICT_GEOFABRIK

LOGGER = logging.getLogger(__name__)
DATA_DIR = '' #TODO: what should be default data dir? create one in parent dir. eg. osm-data? and put in constants (though rather config?)

# =============================================================================
#  DOWNLOAD METHODS
# =============================================================================

def _create_gf_download_url(iso3, file_format):
    """
    create string with download-url from geofabrik

    Parameters
    ----------
    iso3 : str
        ISO3 code of country to download
    file_format : str
        Format in which file should be downloaded; ESRI Shapefiles ('shp')
        or osm-Protocolbuffer Binary Format ('pbf')

    Returns
    -------
    str : Geofabrik download-string for the requested country.

    See also
    --------
    DICT_GEOFABRIK for exceptions / special regions.
    """
    try:
        if file_format == 'shp':
            return f'{GEOFABRIK_URL}{DICT_GEOFABRIK[iso3][0]}/{DICT_GEOFABRIK[iso3][1]}-latest-free.shp.zip'
        if file_format == 'pbf':
            return f'{GEOFABRIK_URL}{DICT_GEOFABRIK[iso3][0]}/{DICT_GEOFABRIK[iso3][1]}-latest.osm.pbf'
    except KeyError:
        if iso3=='RUS':
            raise KeyError("""Russia comes in two files. Please specify either
                         'RUS-A for the Asian or RUS-E for the European part.""")
        raise KeyError("""The provided iso3 seems not to be available on
                           Geofabrik.de. You can clip it from the planet
                           file or an adequate regional file, instead. See
                           the methods in the clip module for this.""")

    return LOGGER.error('invalid file format. Please choose one of [shp, pbf]')

# TODO: rename to get_country_geofabrik; include an override=False kwarg
# TODO: decide whether to issue warnings for multi-country files
def get_data_geofabrik(iso3, file_format='pbf', save_path=DATA_DIR):
    """
    Download country files with all OSM map info from the provider
    Geofabrik.de, if doesn't exist, yet.

    Parameters
    ----------
    iso3 : str
        ISO3 code of country to download
        Exceptions: Russia is divided into European and Asian part
        ('RUS-E', 'RUS-A'), Canary Islands are 'IC'.
    file_format : str
        Format in which file should be downloaded; options are
        ESRI Shapefiles (shp), which can easily be loaded into gdfs,
        or osm-Protocolbuffer Binary Format (pbf), which is smaller in
        size, but has a more complicated query syntax to load (functions
        are provided in the OSMFileQuery class).
    save_path : str or pathlib.Path
        Folder in which to save the file

    Returns
    -------
    None
        File is downloaded and stored under save_path + the Geofabrik filename

    See also
    --------
    DICT_GEOFABRIK for exceptions / special regions.
    """

    download_url = _create_gf_download_url(iso3, file_format)
    local_filepath = Path(save_path , download_url.split('/')[-1])
    if not Path(local_filepath).is_file():
        LOGGER.info(f'Downloading file as {local_filepath}')
        urllib.request.urlretrieve(download_url, local_filepath)
    else:
        LOGGER.info(f'file already exists as {local_filepath}')

# TODO: write up
def get_region_geofabrik(iso3, file_format='pbf', save_path=DATA_DIR):
    pass
    


def get_data_planet(save_path=Path(DATA_DIR,'planet-latest.osm.pbf')):
    """
    Download the entire planet file from the OSM server (ca. 60 GB).

    Parameters
    ----------
    save_path : str or pathlib.Path
    """

    if not Path(save_path).is_file():
        LOGGER.info(f'Downloading file as {save_path}')
        urllib.request.urlretrieve(PLANET_URL, save_path)
    else:
        LOGGER.info(f'file already exists as {save_path}')
