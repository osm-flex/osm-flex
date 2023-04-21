#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraction functions
"""

import logging
import geopandas as gpd
from osgeo import ogr, gdal
import pandas as pd
from pathlib import Path
import shapely
from tqdm import tqdm

from osm_flex.config import DICT_CIS_OSM, OSM_CONFIG_FILE


LOGGER = logging.getLogger(__name__)
DATA_DIR = '' #TODO: dito, where & how to define
gdal.SetConfigOption("OSM_CONFIG_FILE", str(OSM_CONFIG_FILE))


def _query_builder( geo_type, constraint_dict):
    """
    This function builds an SQL query from the values passed to the extract()
    function.

    Parameters
    ---------
    geo_type : str
        Type of geometry to extract. One of [points, lines, multipolygons]
    constraint_dict :  dict

    Returns
    -------
    query : str
        an SQL query string.
    """
    # columns which to report in output
    query =  "SELECT osm_id"
    for key in constraint_dict['osm_keys']:
        query+= ","+ key
    # filter condition(s)
    query+= " FROM " + geo_type + " WHERE " + constraint_dict['osm_query']

    return query

def extract(osm_path, geo_type, osm_keys, osm_query):
    """
    Function to extract geometries and tag info for entires in the OSM file
    matching certain OSM key-value constraints.
    from an OpenStreetMap osm.pbf file.

    Parameters
    ----------
    osm_path : str or Path
        location of osm.pbf file from which to parse
    geo_type : str
        Type of geometry to extract. One of [points, lines, multipolygons]
    osm_keys : list
        a list with all the osm keys that should be reported as columns in
        the output gdf.
    osm_query : str
        query string of the syntax
        "key(='value') (and/or further queries)".
        See examples in DICT_CIS_OSM in case of doubt.

    Returns
    -------
    gpd.GeoDataFrame
        A gdf with all results from the osm.pbf file matching the
        specified constraints.

    Note
    ----
    1) The keys that are searchable are specified in the osmconf.ini file.
    Make sure that they exist in the attributes=... paragraph under the
    respective geometry section.
    For example, to extract multipolygons with building='yes',
    building must be in the attributes under
    the [multipolygons] section of the file. You can find it in the same
    folder as the osm_dataloader.py module is located.
    2) OSM keys that have : in their name must be changed to _ in the
    search dict, but not in the osmconf.ini
    E.g. tower:type is called tower_type, since it would interfere with the
    SQL syntax otherwise, but still tower:type in the osmconf.ini

    See also
    --------
    https://taginfo.openstreetmap.org/ to check what keys and key/value
    pairs are valid.
    https://overpass-turbo.eu/ for a direct visual output of the query,
    and to quickly check the validity. The wizard can help you find the
    correct keys / values you are looking for.
    """
    if not Path(osm_path).is_file():
        raise ValueError(f"the given path is not a file: {osm_path}")
    
    osm_path = str(osm_path)
    constraint_dict = {
        'osm_keys' : osm_keys,
        'osm_query' : osm_query}

    driver = ogr.GetDriverByName('OSM')
    data = driver.Open(osm_path)
    query = _query_builder(geo_type, constraint_dict)
    LOGGER.debug("query: %s", query)
    sql_lyr = data.ExecuteSQL(query)
    features = []
    if data is not None:
        LOGGER.info('query is finished, lets start the loop')
        for feature in tqdm(sql_lyr, desc=f'extract {geo_type}'):
            try:
                fields = [feature.GetField(key) for key in
                          ['osm_id', *constraint_dict['osm_keys']]]
                wkb = feature.geometry().ExportToWkb()
                geom = shapely.wkb.loads(bytes(wkb))
                if geom is None:
                    continue
                fields.append(geom)
                features.append(fields)
            except Exception as exc:
                LOGGER.info('%s - %s', exc.__class__, exc)
                LOGGER.warning("skipped OSM feature")
    else:
        LOGGER.error("""Nonetype error when requesting SQL. Check the
                     query and the OSM config file under the respective
                     geometry - perhaps key is unknown.""")

    return gpd.GeoDataFrame(
        features, columns=['osm_id', *constraint_dict['osm_keys'], 'geometry'],
        crs='epsg:4326')

# TODO: decide on name of wrapper, which categories included & what components fall under it.
def extract_cis(osm_path, ci_type):
    """
    A wrapper around extract() to conveniently extract map info for a
    selection of  critical infrastructure types from the given osm.pbf file.
    No need to search for osm key/value tags and relevant geometry types.
    Parameters
    ----------
    osm_path : str or Path
        location of osm.pbf file from which to parse
    ci_type : str
        one of DICT_CIS_OSM.keys(), i.e. 'education', 'healthcare',
        'water', 'telecom', 'road', 'rail', 'air', 'gas', 'oil', 'power',
        'wastewater', 'food'
    See also
    -------
    DICT_CIS_OSM for the keys and key/value tags queried for the respective
    CIs. Modify if desired.
    """
    # features consisting in points and multipolygon results:
    if ci_type in ['healthcare','education','food', 'buildings']:
        gdf = pd.concat([
            extract(osm_path, 'points', DICT_CIS_OSM[ci_type]['osm_keys'],
                    DICT_CIS_OSM[ci_type]['osm_query']),
            extract(osm_path, 'multipolygons', DICT_CIS_OSM[ci_type]['osm_keys'],
                    DICT_CIS_OSM[ci_type]['osm_query'])
            ])

    # features consisting in multipolygon results:
    elif ci_type in ['air']:
        gdf = extract(osm_path, 'multipolygons', 
                      DICT_CIS_OSM[ci_type]['osm_keys'],
                      DICT_CIS_OSM[ci_type]['osm_query'])

    # features consisting in points, multipolygons and lines:
    elif ci_type in ['gas','oil','telecom','water','wastewater','power',
                     'rail','road', 'main_road']:
        gdf =  pd.concat([
            extract(osm_path, 'points', DICT_CIS_OSM[ci_type]['osm_keys'],
                    DICT_CIS_OSM[ci_type]['osm_query']),
            extract(osm_path, 'multipolygons', DICT_CIS_OSM[ci_type]['osm_keys'],
                             DICT_CIS_OSM[ci_type]['osm_query']),
            extract(osm_path, 'lines', DICT_CIS_OSM[ci_type]['osm_keys'],
                             DICT_CIS_OSM[ci_type]['osm_query'])
            ])
    else:
        LOGGER.warning('feature not in DICT_CIS_OSM. Returning empty gdf')
        gdf = gpd.GeoDataFrame()
    return gdf