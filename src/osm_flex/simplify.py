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

import geopandas as gpd
import numpy as np

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

    gdf_temp['geometry'] = gdf_temp.apply(lambda row: make_valid(row.geometry),
                                          axis=1)

    return gdf_temp[(gdf_temp['geometry'].area > min_area) |
                    (gdf_temp['geometry'].area == 0)]


def remove_contained_points(gdf_p_mp):
    """
    from a GeoDataFrame containing points and (multi-)polygons, remove those
    points that are contained in a multipolygons entry.
    Resets the index of the dataframe.

    Parameters
    ----------
    gdf_p_mp : gpd.GeoDataFrame
        GeoDataFrame containing entries with point and (multi-)polygon geometry
    """

    gdf_p_mp = gdf_p_mp.reset_index(drop=True)

    ind_dupl = np.unique(gpd.sjoin(gdf_p_mp[gdf_p_mp.geometry.type=='Point'],
              gdf_p_mp[(gdf_p_mp.geometry.type=='MultiPolygon')|
                       (gdf_p_mp.geometry.type=='Polygon')],
              predicate='within').index)

    return gdf_p_mp.drop(index=ind_dupl)


def remove_contained_polys(gdf):
    """
    from a GeoDataFrame containing (multi-)polygons (and potentially other
    geometries), remove those polygon entries that are already fully
    contained in another polygon entries. Removes smaller polygons within 
    polygons and full duplicates, but leaves contained points untouched 
    (see remove_contained_points() for this).

    Resets the index of the dataframe.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing entries with (multi-)polygon geometry
    """

    gdf = gdf.reset_index(drop=True)

    contained = gpd.sjoin(
        gdf[(gdf.geometry.type=='MultiPolygon')| (gdf.geometry.type=='Polygon')],
        gdf[(gdf.geometry.type=='MultiPolygon')| (gdf.geometry.type=='Polygon')],
        predicate='contains'
        )

    subset = contained[contained.index != contained.index_right]
    to_drop = set(subset.index_right) - set(subset.index)

    return gdf.drop(index=to_drop)


def remove_exact_duplicates(gdf):
    """
    from a GeoDataFrame containing any sort of geometries, remove those entries
    which already have an exact duplicate geometry entry.

    Resets the index of the dataframe.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing any types of geometry
    """

    gdf = gdf.reset_index(drop=True)

    geom_wkb = gdf["geometry"].apply(lambda geom: geom.wkb)

    return gdf.loc[geom_wkb.drop_duplicates().index]
