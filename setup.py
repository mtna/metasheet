#!/usr/bin/env python
#
# References:
# https://setuptools.pypa.io/en/latest/userguide/index.html
# https://setuptools.pypa.io/en/latest/userguide/quickstart.html#including-data-files
# https://packaging.python.org/en/latest/guides/using-manifest-in/
# https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
#
# to update requirements.txt: pipreqs --force metasheet
# to build:  ./setup.py build
# to install: ./setup.py install
# to release: ./setup.py release sdist bdist_wheel (release is an alias)
# to publish:  twine upload dist/* (need user and password, add --repository testpypi for testing)
# 
# development mode on: ./setup.py develop
# development mode off: ./setup.py develop -u
#

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='metasheet',  # Required
    version='0.2.2',  # Required
    classifiers=[  # Optional
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    description='Metasheet parser, serializers, and repository manager',
    author='Pascal Heus',
    author_email='pascal.heus@mtna.us',
    include_package_data=True,
    install_requires=['openpyxl','python_dateutil'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    #url='https://github.com/mtna/metasheet',
    project_urls={  # Optional
        'Maintainer': 'http://www.mtna.us',
    },
    python_requires=">=3.6",    
    scripts=['bin/metasheet']
    )


