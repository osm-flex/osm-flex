#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clipping functions
"""

import logging
import numpy as np
from pathlib import Path
import shapely
import subprocess
from cartopy.io import shapereader
from .config import POLY_DIR

from osm_flex.config import POLY_DIR
LOGGER = logging.getLogger(__name__)

# Elco originally used GADM36 country & adminX files etc. -->
# see osm_clipper repo.

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


def _shapely2poly(geom_list, filename, save_path=POLY_DIR):
    """
    Convert list of shapely (multi)polygon(s) into .poly files needed for
    osmosis to generate cut-outs from bigger osm.pbf files
    Saves the hence created file under save_path.

    Parameters
    ---------
    geom_list : list
        list of polygon, polygons or multipolygons containing a (complex) shape
        to be cut out of a bigger file
    filename : str
        filename
    save_path : pathlib.Path or str
        path under which the created file is to bestored

    Returns
    -------
    None

    Note
    ----
    For more info on what .poly files are (incl. several tools for
    creating them), see
    https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
    """
    filename = Path(save_path).joinpath(filename).with_suffix('.poly')
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


# TODO: clipping functions included only for osmosis. Elco prefers osmconvert.
# include both and let user choose which one run under the hood? or just osmconvert.
# osm_clipper for respective functions.

def _build_osmosis_cmd(shape, path_parentfile, path_clip):

     if isinstance(shape[0], (float, int)):
         return['osmosis', '--read-pbf', 'file='+str(path_parentfile),
                '--bounding-box', f'top={shape[3]}', f'left={shape[0]}',
                f'bottom={shape[1]}', f'right={shape[2]}',
                '--write-pbf', 'file='+str(path_clip)]
     if isinstance(shape[0], str):
         return ['osmosis', '--read-pbf', 'file='+str(path_parentfile),
                '--bounding-polygon', 'file='+shape, '--write-pbf',
                'file='+str(path_clip)]

     raise ValueError('''shape does not have the correct format.
                           Only bounding boxes or filepaths to .poly
                           files are allowed''')

# TODO: all functions here should be called clip not extract, to be consistent with
# terminology (clipping = cutting, extracting = parsing)
def _osmosis_clip(shape, path_parentfile, path_clip,
                      overwrite=False):
     """
     Runs the command line tool osmosis to cut out all map info within
     shape (bounding box or poygon(s)), from a bigger parent file, unless
     file already exists.

     If your device doesn't have osmosis yet, see installation instructions:
     https://wiki.openstreetmap.org/wiki/Osmosis/Installation

     Parameters
     -----------
     shape : list or str
         list containing [xmin, ymin, xmax, ymax] for a bounding box  or
         a string to the .poly file path delimiting the bounds.
     path_parentfile : str or pathlib.Path
         file path to planet.osm.pbf or other osm.pbf file to extract from
     path_clip : str or pathlib.Path
         file path (incl. name & ending osm.pbf) under which extract will be stored
     overwrite : bool
         default is False. Whether to overwrite files if they already exist.

     Returns
     -------
     None or subprocess
     """

     if ((not Path(path_clip).is_file()) or
         (Path(path_clip).is_file() and overwrite)):

         LOGGER.info("""File doesn`t yet exist or overwriting old one.
                     Assembling osmosis command.""")

         cmd = _build_osmosis_cmd(shape, path_parentfile, path_clip)

         LOGGER.info('''Extracting from larger file...
                     This will take a while''')

         return subprocess.run(cmd, stdout=subprocess.PIPE,
                               universal_newlines=True)

     LOGGER.info("Extracted file already exists!")
     return None


def clip_from_bbox(bbox, path_clip,
                   path_parentfile=Path(POLY_DIR, 'planet-latest.osm.pbf'),
                   overwrite=False):
     """
     get OSM raw data from abounding-box, which is extracted
     from a bigger (e.g. the planet) file.

     Parameters
     ----------
     bbox : list
         bounding box [xmin, ymin, xmax, ymax]
     path_clip : str or pathlib.Path
         file path (incl. name & ending) under which extract will be stored
     path_planet : str or pathlib.Path
         file path to planet-latest.osm.pbf. Will download & store it as
         indicated, if doesn`t yet exist.
         Default is DATA_DIR/planet-latest.osm.pbf
     overwrite : bool
         default is False. Whether to overwrite files if they already exist.

     Note
     ----
     This function uses the command line tool osmosis to cut out new
     osm.pbf files from the original ones.
     Installation instructions (windows, linux, apple) - see
     https://wiki.openstreetmap.org/wiki/Osmosis/Installation
     """
     if not Path(path_parentfile).is_file():
         LOGGER.error("Paret file wasn't found.")
     _osmosis_clip(bbox, path_parentfile, path_clip, overwrite)


def clip_from_poly(path_poly, path_clip,
                   path_parentfile=Path(POLY_DIR, 'planet-latest.osm.pbf'),
                   overwrite=False):
     """
     get OSM raw data from a custom shape defined in .poly file which is extracted
     from the entire OSM planet file. Accepts path to
     .poly files.

     Parameters
     ----------
     path_poly : str
         file path to a .poly file
     path_clip : str or pathlib.Path
         file path (incl. name & ending) under which extract will be stored
     path_parentfile : str or pathlib.Path
         file path to planet-latest.osm.pbf. Will download & store it as
         indicated, if doesn`t yet exist.
         Default is DATA_DIR/planet-latest.osm.pbf
     overwrite : bool
         default is False. Whether to overwrite files if they already exist.

     Note
     ----
     This function uses the command line tool osmosis to cut out new
     osm.pbf files from the original ones.
     Installation instructions (windows, linux, apple) - see
     https://wiki.openstreetmap.org/wiki/Osmosis/Installation
     """

     if not Path(path_parentfile).is_file():
         LOGGER.warning("Parent file wasn't found.")
     _osmosis_clip(path_poly, path_parentfile, path_clip, overwrite)

def clip_from_shapes(shape_list, path_poly, path_clip,
                     path_parentfile=Path(POLY_DIR, 'planet-latest.osm.pbf'),
                     overwrite=False):
     """
     get OSM raw data from a custom shape defined by a list of polygons
     which is extracted from the entire OSM planet file.
     The list of shapes first needs to be converted to a .poly file and then
     passed back to the function (under the hood).

     Parameters
     ----------
     shape_list : list
         list of (Multi-)Polygon(s) that define the shape which should be cut,
         as e.g. obtained
     path_clip : str or pathlib.Path
         file path (incl. name & ending) under which extract will be stored
     path_poly : str
         file path under which the .poly file should be stored that is created
         from the shapes.
     path_parentfile : str or pathlib.Path
         file path to planet-latest.osm.pbf. Will download & store it as
         indicated, if doesn`t yet exist.
         Default is DATA_DIR/planet-latest.osm.pbf
     overwrite : bool
         default is False. Whether to overwrite files if they already exist.

     Note
     ----
     This function uses the command line tool osmosis to cut out new
     osm.pbf files from the original ones.
     Installation instructions (windows, linux, apple) - see
     https://wiki.openstreetmap.org/wiki/Osmosis/Installation
     """

     if not Path(path_parentfile).is_file():
         LOGGER.error("Parent file wasn't found.")

     shape_list = _simplify_shapelist(shape_list)
     _shapely2poly(shape_list, path_poly)
     _osmosis_clip(path_poly, path_parentfile, path_clip,
                           overwrite)
