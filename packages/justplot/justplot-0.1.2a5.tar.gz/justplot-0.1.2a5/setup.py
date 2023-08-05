#!/usr/bin/python
# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name='justplot',
    version='0.1.2a5',
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
    include_package_data=True,
)

