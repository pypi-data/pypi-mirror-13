from distutils.core import setup
from setuptools import find_packages

setup(
    name='oaxmlapi',
    version='1.1',
    author='Ryan Morrissey/Ben Hughes',
    author_email='contactme@ryancmorrissey.com/bwghughes@gmail.com',
    packages=find_packages(),
    url='https://github.com/goincremental/oaxmlapi',
    license='LICENSE',
    description='A Python wrapper around the NetSuite OpenAir XML API.',
    long_description=open('README.md').read(),
    install_requires=[
        "simplejson"
    ],
    zip_safe=False,
)
