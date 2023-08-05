
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='odcantoolkit',
    version='0.1.2',
    description='Python tool to fetch data from Canada\'s open data portal',
    long_description=long_description,

    url='https://github.com/gchamp20/odcantoolkit',

    author='Guillaume Champagne',
    author_email='guillaume.champagne@polymtl.ca',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='canada open data json mongodb',

    packages=find_packages(exclude=['tests']),

    # List run-time dependencies here.
    install_requires=['pymongo'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'odcantoolkit=odcantoolkit:launch',
        ],
    },
)
