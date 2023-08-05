# -*- coding: utf8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'packages': ['umap'],
    'description': 'UNIST synthesis MAP solution',
    'author': 'Kyunghoon Kim',
    'author_email': 'preware@gmail.com',
    'url': 'http://amath.unist.ac.kr',
    'download_url': 'http://github.com/koorukuroo/umap',
    'version': '0.1.1',
    'install_requirements': ['folium', 'vincenty'],
    'scripts': [],
    'py_modules': ['umap.get', 'umap.map'],
    'name': 'umap',
    'include_pakcage_data': True,
    'package_data': {'': ['assets/*.txt']},
    'classifiers': ['Development Status :: 2 - Pre-Alpha',
                    'Programming Language :: Python']
}

setup(**config)
