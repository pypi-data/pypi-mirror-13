#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='epifx',
    version='0.3.0',
    url='https://bitbucket.org/robmoss/epidemic-forecasting-for-python/',
    description='Epidemic forecasting with mechanistic infection models',
    license='BSD 3-Clause License',
    author='Rob Moss',
    author_email='rgmoss@unimelb.edu.au',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cmp-output = epifx.cmp:main'
        ]
    },
    install_requires=[
        'h5py >= 2.2',
        'numpy >= 1.8',
        'pypfilt >= 0.3',
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
)
