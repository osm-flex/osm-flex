"""A setuptools based setup module.
"""

from setuptools import setup, find_packages

setup(
    name='osm-flex',
    version='0.1.0',    
    description='Python package for flexible data extraction from OpenStreetMap',
    url='https://github.com/ElcoK/osm-flex',
    license='GPL-3.0',
    packages= find_packages()+['data'],
    install_requires=['geopandas',
                      'pandas',
                      'numpy', 
                      'shapey',
                      'tqdm'
                      ],
    keywords='OpenStreetMap',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    include_package_data=True
    
)