#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clipping functions
"""

import logging
import numpy as np
import pathlib
import shapely
import subprocess
from cartopy.io import shapereader

from osm_flex.config import POLY_DIR
LOGGER = logging.getLogger(__name__)


def get_admin1_shapes(country):
    """Provide Natural Earth registry info and shape files for countries

    Parameters
    ----------
    country : str
        string of ISO 3166 code

    Returns
    -------
    country_shapes : dict
        Shapes (according to Natural Earth) of admin1 regions of country
        with name as keys
    """

    if not isinstance(country, str):
        LOGGER.error("country needs to be of type str")
        raise TypeError("Invalid type for input parameter 'country'")
    admin1_file = shapereader.natural_earth(resolution='10m',
                                            category='cultural',
                                            name='admin_1_states_provinces')
    admin1_recs = shapereader.Reader(admin1_file)
    admin1_shapes = {}
    for rec in admin1_recs.records():
        if rec.attributes['adm0_a3'] == country:
            name = rec.attributes['name_en']
            admin1_shapes[name] = rec.geometry
    if not admin1_shapes:
        raise LookupError(f'natural_earth records are empty for country {country}')
    return admin1_shapes

def get_country_shape(country):
    """Provide Natural Earth registry info and shape files for admin1 regions
    of chosen country

    Parameters
    ----------
    country : str
        string of ISO 3166 code

    Returns
    -------
    country_shape : (multi-)polygon
        Shape of the country according to Natural Earth.
    """

    if not isinstance(country, str):
        LOGGER.error("country needs to be of type str")
        raise TypeError("Invalid type for input parameter 'country'")
    admin0_file = shapereader.natural_earth(resolution='10m',
                                            category='cultural',
                                            name='admin_0_countries')
    admin0_recs = shapereader.Reader(admin0_file)
    for rec in admin0_recs.records():
        if rec.attributes['ADM0_A3'] == country:
            return rec.geometry
    raise LookupError(f'natural_earth records are empty for country {country}')


def _simplify_shapelist(geom_list, thres=None):
    """
    remove tiny shapes and simplify outlines to save on file size for
    .poly files
    """
    if thres is None:
        thresh = 0.1 if shapely.ops.unary_union(geom_list).area > 1 else 0.01
    geom_list = [geom for geom in geom_list if geom.area>thresh]
    return [geom.simplify(tolerance=0.01, preserve_topology=True) for
            geom in geom_list]


def _shapely2poly(geom_list, filename):
    """
    Convert list of shapely (multi)polygon(s) into .poly files needed for
    osmosis to generate cut-outs from bigger osm.pbf files.

    Parameters
    ---------
    geom_list : list
        list of polygon, polygons or multipolygons containing a (complex) shape
        to be cut out of a bigger file
    filename : pathlib.Path or str
        output filename including directory path.

    Returns
    -------
    None

    Note
    ----
    For more info on what .poly files are (incl. several tools for
    creating them), see
    https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
    """
    filename = pathlib.Path(filename).with_suffix('.poly')
    if filename.exists():
        raise ValueError(f'File {filename} already exists, aborting.')

    # start writing the .poly file
    file = open(filename, 'w')
    file.write('Polygons' + "\n")

    # loop over the different polygons, get their exterior and write the
    # coordinates of the ring to the .poly file
    i = 0
    for shape in geom_list:
        if shape.geom_type == 'MultiPolygon':
            polygons = shape.geoms
        elif shape.geom_type == 'Polygon':
            polygons = [shape]

        for polygon in polygons:
            polygon = np.array(polygon.exterior.coords)
            file.write(str(i) + "\n")
            i += 1
            for ring in polygon:
                file.write("    " + str(ring[0]) + "     " + str(ring[1]) +"\n")

            # close the ring of one subpolygon if done
            file.write("END" +"\n")

    # close the file when done
    file.write("END" +"\n")
    file.close()

def _build_osmosis_cmd(shape, osmpbf_clip_from, osmpbf_output):
    """
    builds osmosis command for clipping

    Parameters
    -----------
    shape : list or str or pathlib.Path
        list containing [xmin, ymin, xmax, ymax] for a bounding box or
        a string/Path to the .poly file path delimiting the bounds.
    osmpbf_clip_from: str or pathlib.Path
        file path to planet.osm.pbf or other osm.pbf file to clip
    osmpbf_output : str or pathlib.Path
        file path (incl. name & ending) under which extract will be stored
    """
    if isinstance(shape, (pathlib.PosixPath, str)):
        return ['osmosis', '--read-pbf', 'file='+str(osmpbf_clip_from),
            '--bounding-polygon', 'file='+str(shape), '--write-pbf',
            'file='+str(osmpbf_output)]
    if isinstance(shape[0], (float, int)):
        return['osmosis', '--read-pbf', 'file='+str(osmpbf_clip_from),
            '--bounding-box', f'top={shape[3]}', f'left={shape[0]}',
            f'bottom={shape[1]}', f'right={shape[2]}',
            '--write-pbf', 'file='+str(osmpbf_output)]

    raise ValueError('''shape does not have the correct format.
                        Only bounding boxes or filepaths to .poly
                        files are allowed''')

def _osmosis_clip(shape, osmpbf_clip_from, osmpbf_output,
                  overwrite=False):
    """
    Runs the command line tool osmosis to cut out all map info within
    shape (bounding box or poygon(s)), from a bigger parent file, unless
    file already exists.

    If your device doesn't have osmosis yet, see installation instructions:
    https://wiki.openstreetmap.org/wiki/Osmosis/Installation

    Parameters
    -----------
    shape : list or str or pathlib.Path
        list containing [xmin, ymin, xmax, ymax] for a bounding box or
        a string/Path to the .poly file path delimiting the bounds.
    osmpbf_clip_from: str or pathlib.Path
        file path to planet.osm.pbf or other osm.pbf file to clip
    osmpbf_output : str or pathlib.Path
        file path (incl. name & ending) under which extract will be stored
    overwrite : bool
        default is False. Whether to overwrite files if they already exist.

    Returns
    -------
    None or subprocess
    """
    osmpbf_clip_from = pathlib.Path(osmpbf_clip_from)
    if not osmpbf_clip_from.suffix:
        osmpbf_clip_from = osmpbf_clip_from.with_suffix('.osm.pbf')
    if not osmpbf_clip_from.is_file():
        raise ValueError(f"OSM file {osmpbf_clip_from} to clip from not found.")

    if ((not pathlib.Path(osmpbf_output).is_file()) or
        (pathlib.Path(osmpbf_output).is_file() and overwrite)):

        LOGGER.info("""File doesn`t yet exist or overwriting old one.
                    Assembling osmosis command.""")

        cmd = _build_osmosis_cmd(shape, osmpbf_clip_from, osmpbf_output)

        LOGGER.info('''Extracting from larger file...
                    This will take a while''')

        return subprocess.run(cmd, stdout=subprocess.PIPE,
                            universal_newlines=True)

    raise ValueError(f"File {osmpbf_output} already exists. Abort.")


def clip_from_bbox(bbox, osmpbf_clip_from, osmpbf_output,
                   overwrite=False, kernel='osmosis'):
    """
    get OSM raw data from abounding-box, which is extracted
    from a bigger (e.g. the planet) file.

    Parameters
    ----------
    bbox : list
        bounding box [xmin, ymin, xmax, ymax]
    osmpbf_clip_from: str or pathlib.Path
        file path to planet.osm.pbf or other osm.pbf file to clip
    osmpbf_output : str or pathlib.Path
        file path (incl. name & ending) under which extract will be stored
    overwrite : bool
        default is False. Whether to overwrite files if they already exist.
    kernel : str
        name of the clipping kernel: 'osmconvert' or 'osmosis'
        Default is 'osmosis'.
    Note
    ----
    This function uses the command line tool osmosis to cut out new
    osm.pbf files from the original ones.
    Installation instructions (windows, linux, apple) - see
    https://wiki.openstreetmap.org/wiki/Osmosis/Installation
    """
    # TODO: allow for osmpbf_output to be only file name & save in default DIR
    # TODO: avoid returning None
    if kernel == 'osmosis':
        _osmosis_clip(bbox, osmpbf_clip_from, osmpbf_output, overwrite)
        return None
    elif kernel == 'osmconvert':
        raise NotImplementedError()
    raise ValueError(f"Kernel '{kernel}' is not valid. Abort.")


def clip_from_poly(poly_file, osmpbf_output, osmpbf_clip_from,
                   overwrite=False, kernel='osmosis'):
    """
    get OSM raw data from a custom shape defined in .poly file which is clipped
    from a .osm.pbf file.

    Parameters
    ----------
    poly_file : str
        file path to a .poly file
    osmpbf_output : str or pathlib.Path
        file path (incl. name & ending) under which extract will be stored
    clip_from_file : str or pathlib.Path
        file path to planet-latest.osm.pbf. Will download & store it as
        indicated, if doesn`t yet exist.
        Default is DATA_DIR/planet-latest.osm.pbf
    overwrite : bool
        default is False. Whether to overwrite files if they already exist.
    kernel : str
        name of the clipping kernel: 'osmconvert' or 'osmosis'
        Default is 'osmosis'.

    Note
    ----
    This function uses by default the command line tool osmosis
    to cut out new osm.pbf files from the original ones.
    Installation instructions (windows, linux, macos) - see
    https://wiki.openstreetmap.org/wiki/Osmosis/Installation
    """
    # TODO: avoid returning None
    # TODO: allow for osmpbf_output to be only file name & save in default DIR
    if kernel == 'osmosis':
        _osmosis_clip(poly_file, osmpbf_clip_from, osmpbf_output, overwrite)
        return None
    elif kernel == 'osmconvert':
        raise NotImplementedError()
    raise ValueError(f"Kernel '{kernel}' is not valid. Abort.")


def clip_from_shapes(shape_list, osmpbf_output, osmpbf_clip_from,
                     overwrite=False, kernel='osmosis'):
    """
    get OSM raw data from a custom shape defined by a list of polygons
    which is extracted from the entire OSM planet file.
    The list of shapes first needs to be converted to a .poly file and then
    passed back to the function (under the hood, a temporary file is created
    and deleted upon completion again).

    Parameters
    ----------
    shape_list : list
        list of (Multi-)Polygon(s) that define the shape which should be cut,
        as e.g. obtained
    osmpbf_output : str
        Full file path under which the clipped data will be stored.
    osmpbf_clip_from : str or pathlib.Path
        file path (including filename) to the *.osm.pbf file to clip from.
    overwrite : bool
        default is False. Whether to overwrite files if they already exist.
    kernel : str
        name of the clipping kernel: 'osmconvert' or 'osmosis'
        Default is 'osmosis'.

    Note
    ----
    This function uses the command line tool osmosis to cut out new
    osm.pbf files from the original ones.
    Installation instructions (windows, linux, apple) - see
    https://wiki.openstreetmap.org/wiki/Osmosis/Installation
    """

    shape_list = _simplify_shapelist(shape_list)

    poly_file = POLY_DIR / 'temp_shp.poly'

    _shapely2poly(shape_list, poly_file)
    if kernel == 'osmosis':
        _osmosis_clip(poly_file, osmpbf_clip_from, osmpbf_output, overwrite)
        poly_file.unlink()
        # TODO: avoid returning None
        # TODO: allow for osmpbf_output to be only file name & save in default DIR
        return None
    elif kernel == 'osmconvert':
        poly_file.unlink()
        raise NotImplementedError()
    poly_file.unlink()

    raise ValueError(f"Kernel '{kernel}' is not valid. Abort.")
