#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init file
"""

from pathlib import Path
from .config import OSM_DIR, OSM_DATA_DIR, POLY_DIR, EXTRACT_DIR


def setup_osm_dirs():
    """
    This function is called when osm-flex is imported.
    It creates an osm directory by default in the home directory,
    with three sub-folders osm_bpf, poly and extract, for raw data dumps,
    .poly files, and extraction results, respectively.
    Other locations can be configured in the osm-flex.config file.
    
    Parameters
    ----------
    """
    OSM_DIR.mkdir(parents=True, exist_ok=True)
    for dirpath in [OSM_DATA_DIR, POLY_DIR, EXTRACT_DIR]:
        Path(dirpath).mkdir(parents=True, exist_ok=True)

setup_osm_dirs()
