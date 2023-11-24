# osm-flex

<img align="right" width="200" alt="Logo" src="https://raw.githubusercontent.com/osm-flex/osm-flex/develop/doc/logo_osm-flex.png">

[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/osm-flex/osm-flex)
[![github license badge](https://img.shields.io/github/license/osm-flex/osm-flex)](https://github.com/osm-flex/osm-flex)
[![PyPI version](https://badge.fury.io/py/osm-flex.svg)](https://badge.fury.io/py/osm-flex) 
[![PyPI - Downloads](https://img.shields.io/pypi/dm/osm-flex?color=yellow&label=Downloads)](https://pypistats.org/packages/osm-flex)
[![Documentation Status](https://readthedocs.org/projects/osm-flex/badge/?version=latest)](https://osm-flex.readthedocs.io/en/latest/?badge=latest)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8082963.svg)](https://doi.org/10.5281/zenodo.8082963)

Python package for flexible data extraction from OpenStreetMap. This packages allows to 

1. download OSM data dumps
2. [optional] clip to desired shape
3. extract specific features to geodataframes
4. [optional] simplify results based on geospatial operations

## Documentation

Please refer to the [ReadTheDocs](https://osm-flex.readthedocs.io/en/latest/?badge=latest) of this project for the full documentation of all functions.

## Installation

```
conda create -n osm-flex cartopy geopandas
conda activate osm-flex
pip install osm-flex
```

---
NOTE

This package requires shapely v2.0 or later. Installing this package in an existing environment might overwrite older versions. 


The (optional) clipping functionalities require manual installation of osmconvert or osmosis. See tutorial 1 for details.

---

## Example
Download osm data for Switzerland from geofabrik.

```python
import osm_flex.download as dl

iso3 = 'CHE'
dl.get_country_geofabrik(iso3)
```

Extract all buildings related to education and extract all polygons with forests.

```python
import osm_flex.extract as ex
from osm_flex.config import OSM_DATA_DIR

path_che_dump = OSM_DATA_DIR.joinpath('switzerland-latest.osm.pbf')              
```

```python
gdf_ch_education = ex.extract_cis(path_che_dump, 'education')    
```
<img title="Education" alt="Education GeodataFrame" src="./doc/education_ch.png">


```python
gdf_ch_forest = ex.extract(
	path_che_dump, 'multipolygons', ['landuse', 'name'], "landuse='forest'"
	)    
```

<img title="Forests" alt="Forest map " src="./doc/forest_ch.png">

Drop all education building units that are contained within larger education buildings.

```python
import osm_flex.simplify as sy
gdf_ch_education = sy.rremove_contained_polys(gdf_ch_education)
```

## Running Tests

Follow installation instructions. Then,
```
python -m pip install -e "./[tests]"
pytest
```
