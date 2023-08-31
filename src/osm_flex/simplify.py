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
simplification functions
"""

def remove_small_polygons(gdf, min_area):
    """Remove (multi-)polygons of area smaller than min_area
    Points and lines are untouched.

    Note: a buffer of 1e-10 is added to invalid geometries

    Parameters
    ----------
    gdf : GeoDataFrame
        geodataframe with polygons
    min_area : float
        minimal value of area

    Return
    ------
    GeoDataFrame:
        entry geodataframe without (multi-)polygons smaller than min_area
    """

    gdf_temp = gdf.copy()

    def make_valid(geometry):
        if geometry.is_valid:
            return geometry
        return geometry.buffer(1e-10)

    gdf_temp['geometry'] = gdf_temp.apply(lambda row: make_valid(row.geometry), axis=1)

    return gdf_temp[(gdf_temp['geometry'].area > min_area) | (gdf_temp['geometry'].area == 0)]

