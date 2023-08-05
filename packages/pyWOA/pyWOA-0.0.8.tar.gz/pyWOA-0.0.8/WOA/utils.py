# -*- coding: utf-8 -*-

"""

"""

import os
import sys
import shutil
import hashlib
from tempfile import NamedTemporaryFile

#from filelock import FileLock

if sys.version_info >= (3, 0):
    from urllib.request import urlopen
    from urllib.parse import urlparse
else:
    from urllib2 import urlopen
    from urlparse import urlparse


def woa_dir():
    return os.path.expanduser(os.getenv('WOA_DIR', '~/.woarc'))

def download_file(url, md5hash, dbpath):
    """ Download data file from web

        Copied from CoTeDe.

        IMPROVE it to automatically extract gz files
    """
    download_block_size = 2 ** 16

    assert type(md5hash) is str

    if not os.path.exists(dbpath):
        os.makedirs(dbpath)

    hash = hashlib.md5()

    fname = os.path.join(dbpath, os.path.basename(urlparse(url).path))
    if os.path.isfile(fname):
        h = hashlib.md5(open(fname, 'rb').read()).hexdigest()
        if h == md5hash:
            print("Was previously downloaded: %s" % fname)
            return
        else:
            assert False, "%s already exist but doesn't match the hash: %s" % \
                    (fname, md5hash)

    remote = urlopen(url)

    with NamedTemporaryFile(delete=False) as f:
        try:
            bytes_read = 0
            block = remote.read(download_block_size)
            while block:
                f.write(block)
                hash.update(block)
                bytes_read += len(block)
                block = remote.read(download_block_size)
        except:
            if os.path.exists(f.name):
                os.remove(f.name)
                raise

    h = hash.hexdigest()
    if h != md5hash:
        os.remove(f.name)
        print("Downloaded file doesn't match. %s" % h)
        assert False, "Downloaded file (%s) doesn't match with expected hash (%s)" % \
                (fname, md5hash)

    shutil.move(f.name, fname)
    print("Downloaded: %s" % fname)


files_db = {'TEMP': {
    5: {
        'url': 'http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/temperature_seasonal_5deg.nc',
        'md5': '271f66e8dea4dfef7db99f5f411af330'
        }
    },
    'PSAL': {
        5: {
            'url': 'http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/salinity_seasonal_5deg.nc',
            'md5': '1d2d1982338c688bdd18069d030ec05f'
            }
        }
    }


def datafile(var, resolution=5):
    dbpath = woa_dir()
    cfg = files_db[var][resolution]
    #with FileLock(fname):
    download_file(cfg['url'], cfg['md5'], dbpath)
    datafile = os.path.join(dbpath,
            os.path.basename(urlparse(cfg['url']).path))

    return datafile
