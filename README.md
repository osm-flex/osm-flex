# osm-flex

[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/osm-flex/osm-flex)
[![github license badge](https://img.shields.io/github/license/osm-flex/osm-flex)](https://github.com/osm-flex/osm-flex)
[![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![PyPI version](https://badge.fury.io/py/osm-flex.svg)](https://badge.fury.io/py/osm-flex) 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2551015.svg)](https://doi.org/10.5281/zenodo.2551015) 
[![PyPI - Downloads](https://img.shields.io/pypi/dm/damagescanner?color=yellow&label=Downloads)](https://pypistats.org/packages/osm-flex)
[![Documentation Status](https://readthedocs.org/projects/osm-flex/badge/?version=latest)](https://osm-flex.readthedocs.io/en/latest/?badge=latest)

Python package for flexible data extraction from OpenStreetMap. This packages allows to 

1. download OSM data dumps
2. [optional] clip to desired shape
2. extract specific features to geodataframes

## Installation

```
conda create -n osm-flex cartopy geopandas
conda activate osm-flex
pip install osm-flex
```

---
NOTE

This package requires shapely v2.0 or later. Installing this package in an existing environment might overwrite older versions. 

---

## Example
Download osm data for Switzerland from geofabrik.

```
import osm_flex.download as dl

iso3 = 'CHE'
dl.get_country_geofabrik(iso3)
```

Extract all buildings related to education and extract all polygons with forests.

```
import osm_flex.extract as ex
from osm_flex.config import OSM_DATA_DIR

path_che_dump = OSM_DATA_DIR.joinpath('switzerland-latest.osm.pbf')

gdf_ch_education = extract_cis(path_che_dump, 'education')

gdf_ch_forest = ex.extract(
	path_che_dump, 'multipolygons', ['landuse', 'name'], "landuse='forest'"
	)                      
```



## Running Tests

Follow installation instructions. Then,
```
python -m pip install -e "./[tests]"
pytest
```
