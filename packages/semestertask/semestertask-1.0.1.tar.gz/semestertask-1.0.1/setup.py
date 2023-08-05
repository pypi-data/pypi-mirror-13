# setup for zoodle

from setuptools import setup, find_packages
from codecs import open
from os import path

description = 'semester-centric task generation script for taskwarrior'

setup(
    name='semestertask',
    version='1.0.1',
    description=description,
    long_description=description,
    url='https://github.com/peadargrant/semestertask',
    author='Peadar Grant',
    author_email='peadargrant@gmail.com',
    license='GPLv3+',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='taskwarrior',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['tasklib', 'dateutil'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'semestertask=semestertask.semestertask:main',
        ],
    },
)
