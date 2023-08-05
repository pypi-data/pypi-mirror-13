# -*- coding: utf8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'packages': ['umap'],
    'description': 'UNIST synthesis MAP solution',
    'author': 'Kyunghoon Kim',
    'url': 'http://amath.unist.ac.kr',
    'author_email': 'preware@gmail.com',
    'version': '0.1',
    'install_requirements': ['folium', 'vincenty'],
    'scripts': [],
    'py_modules': ['umap.get', 'umap.map'],
    'name': 'umap',
    'include_pakcage_data': True,
    'package_data': {'': ['assets/*.txt']}
}

setup(**config)
