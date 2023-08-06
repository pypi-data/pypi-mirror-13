#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='pypfilt',
    version='0.3.0',
    url='https://bitbucket.org/robmoss/particle-filter-for-python/',
    description='Bootstrap particle filter for epidemic forecasting',
    license='BSD 3-Clause License',
    author='Rob Moss',
    author_email='rgmoss@unimelb.edu.au',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'h5py >= 2.2',
        'numpy >= 1.8',
        'scipy >= 0.11',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
)
