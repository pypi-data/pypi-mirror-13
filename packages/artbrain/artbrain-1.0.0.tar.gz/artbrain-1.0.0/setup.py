from setuptools import setup, find_packages
import codecs
import os

setup(
    # Application name:
    name="artbrain",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="vsoch",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    package_data = {'artbrain.templates':['*.html'],
                    'artbrain.data':['*.pkl']},

    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/vsoch/artbrain",

    license="LICENSE.txt",
    description="embed images into brain imaging data",
    keywords='brain art neuroimaging',

    install_requires = ['numpy','pandas','PyPNG','nibabel','scipy'],

    entry_points = {
        'console_scripts': [
            'artbrain=artbrain.scripts:main',
        ],
    },

)
