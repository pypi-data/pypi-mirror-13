#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-

from distutils.core import setup
import os

long_description = 'A thin wrapper around matplotlib, which lets you save figure and axes settings for reuse.'

if os.path.exists('README.rst'):
    long_description = open('README.rst').read()


setup(
    name='justplot',
    version='0.1.2a10',
    packages=['justplot',],
    license='MIT',
    author='Uğur Çayoğlu',
    author_email='urcyglu@gmail.com',
    description='A thin wrapper around matplotlib, which lets you reuse settings.',
    url='https://github.com/OnionNinja/justplot',
    download_url='https://github.com/onionninja/justplot/tarball/v0.1.2',
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    classifiers=[
        # More at http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
      ],
    keywords=['plots','matplotlib','wrapper'],
    long_description = long_description,
    include_package_data=True,
)

