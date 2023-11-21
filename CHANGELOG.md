# Changelog
## v1.1.0

Release date: 2023-11-21

### Description

Second release. 

### Added
* simplify module for simple cleaning functions of OSM parsing output

### Changed

* clipping with osmconvert can now handle parentfiles > 2 GB

### Fixed

* Fix  [Issue #25](https://github.com/osm-flex/osm-flex/issues/25).
* Fix  [Issue #15](https://github.com/osm-flex/osm-flex/issues/15).

## v1.0.1

Release date: 2023-06-26

### Description

First release. 

### Changed

* Update readme and add graphics.
* Add conf.py for sphinx configuration.
* Add index.rst, requirements.txt, requirements.in for documentation building.
* Add logo.
* Publish [documentation] (https://osm-flex.readthedocs.io/en/latest).

### Fixed

* Fix poxit path on windows [Issue #9](https://github.com/osm-flex/osm-flex/issues/9).


## v0.1.0

Release date: 2023-06-22

### Description

First alpha release.

### Dependency Changes
Added:

* cartopy,
* geopandas,
* gdal,
* numpy,
* shapely>=2.0,
* pandas,
* tqdm,

### Added

Base modules including documentation and unit tests.

* clip
* download
* extract

Config files

* config.py
* osmconfig.ini

github wokflows

* for release on Pypi
