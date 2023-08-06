#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='DjangoLightbox',
    version='0.1.5',
    author='Geert Dekkers',
    author_email='geert@djangowebstudio.nl',
    packages=find_packages(),
    scripts=[],
    url='http://pypi.python.org/pypi/DjangoLightbox/',
    license='LICENSE.txt',
    description='alternative for a full screen javascript lightbox for the django framework',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.5",
    ],
    package_data={
        '': ['*.txt', '*.rst', '*html',],
    },
    include_package_data=True,

    keywords = "lightbox images image presentation",
)