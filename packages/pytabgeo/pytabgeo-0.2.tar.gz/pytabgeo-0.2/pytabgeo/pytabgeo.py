import os
import sys
import socket
import argparse
import hashlib
from math import floor
from struct import unpack
import urllib.request as urllib2

iso = [
    'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO',
    'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ',
    'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI',
    'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS',
    'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD',
    'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN',
    'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ',
    'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE',
    'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK',
    'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF',
    'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ',
    'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM',
    'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM',
    'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM',
    'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN',
    'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC',
    'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY',
    'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK',
    'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS',
    'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA',
    'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP',
    'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG',
    'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT',
    'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW',
    'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI',
    'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS',
    'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF',
    'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO',
    'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UM',
    'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI',
    'VN', 'VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM',
    'ZW', 'XA', 'YU', 'CS', 'AN', 'AA', 'EU', 'AP'
]


def _tabgeoBS(arr_data, ip, step):

    start = 0
    end = len(arr_data) - 1
    upack = {}
    upackPrev = {}

    while True:
        mid = floor((start+end)/2)
        if step:
            data = b'\x00' + arr_data[mid]
            # offset, ip, ccid
            boffset, bip, bccid = unpack('>IBB', data)
            upack = dict(offset=boffset, ip=bip, ccid=bccid)
        else:
            # ip, ccid
            bip, bccid = unpack('<iB', arr_data[mid])
            upack = dict(ip=bip, ccid=bccid)

        ip = int(ip)
        if upack['ip'] == ip:
            return upack

        if (end-start < 0):
            if (ip > upack['ip']):
                return upack
            else:
                return upackPrev
        if upack['ip'] > ip:
            end = mid - 1
        else:
            start = mid + 1
        upackPrev = upack


def _is_ipv4(addr):
    try:
        socket.inet_aton(addr)
        return addr
    except:
        print ('Please, enter valid IP address')
        return False


def getCode(ip):

    if not _is_ipv4(ip):
        return

    ip_array = list(map(int, ip.split('.')))

    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    with open(fpath + '/tabgeo_country_v4.dat', 'rb') as f:
        f.seek((ip_array[0]*256 + ip_array[1])*4)
        index_bin = b'\x00' + f.read(4)
        offset, length = unpack('>IB', index_bin)
        f.seek(offset*5 + 262144)
        bin_t = f.read((length+1)*5)
        sbin_t = [bin_t[i:i+5] for i in range(0, len(bin_t), 5)]

        if offset == 16777215:
            return iso[length]

        data = _tabgeoBS(sbin_t, ip_array[2], True)
        if (data['offset'] == 16777215):
            return iso[data['ccid']]

        if(ip_array[2] > data.ip):
            ip_array[3] == 255

        f.seek(0)
        f.seek((data['offset'] + data['ccid'] + 1) * 2)
        bin_f = f.read((data['ccid'] + 1) * 2)
        sbin_f = [bin_f[i:i+2] for i in range(0, len(bin_f), 2)]
        data = _tabgeoBS(sbin_f, ip_array[3], False)

        return iso[data['ccid']]


def syncDB():

    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    resp_md5 = urllib2.urlopen('http://tabgeo.com/api/v4/country/db/md5/')
    hash_md5 = resp_md5.read().decode('utf-8')

    hash_db = hashlib.md5(
        open('tabgeo_country_v4.dat', 'rb').read()).hexdigest()

    if hash_md5 != hash_db:
        res = urllib2.urlopen('http://tabgeo.com/api/v4/country/db/get/')
        db = res.read()
        with open(fpath + '/tabgeo_country_v4.dat', 'wb') as f:
            f.write(db)
            print('Database update.')
    else:
        print('Database dont need update.')



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("ip",
                        nargs="?",
                         help="Enter IP address")

    parser.add_argument("-s", "--sync",
                        action="store_const",
                        const=" ",
                        help="Update database")

    args = parser.parse_args()

    if args.sync:
        syncDB()

    if args.ip:
        if not _is_ipv4(args.ip):
            return

        print('IP address: {0} \nCountry code: {1}'.format(args.ip,\
                                                  getCode(args.ip)))


if __name__ == '__main__':
    main()
