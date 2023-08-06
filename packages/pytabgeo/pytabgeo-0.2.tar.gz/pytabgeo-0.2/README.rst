Overview
--------

Tabgeo - a special geolocation database to determine country of the user according to his IP-address.


Installation
------------

$pip install pytabgeo

Usage:
______

Example usage:

    >>> import pytabgeo
    >>> pytabgeo.getCode('8.8.8.8')
    'US'

    $ python3 pytabgeo.py 8.8.8.8
    IP address: 8.8.8.8 
    Country code: US
