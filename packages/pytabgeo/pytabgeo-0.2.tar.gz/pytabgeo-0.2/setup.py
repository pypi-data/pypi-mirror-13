from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='pytabgeo',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    description='Python driver for TabGeo.com base',
    long_description='Python driver for TabGeo.com base',
    author='axce1',
    author_email='axce1.github@gmail.com',
    platforms='any',
    url='https://github.com/axce1/pytabgeo',
    license='WTFPL',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points = {
        'console_scripts': ['pytabgeo=pytabgeo.pytabgeo:main'],
    },
)
