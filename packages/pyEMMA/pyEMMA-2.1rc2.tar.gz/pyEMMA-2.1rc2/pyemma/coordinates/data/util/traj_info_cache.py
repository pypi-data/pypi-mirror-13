# This file is part of PyEMMA.
#
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Created on 30.04.2015

@author: marscher
'''

from __future__ import absolute_import

from six import PY2
from threading import Semaphore
import os

from pyemma.util.config import conf_values
from logging import getLogger
import numpy as np

logger = getLogger(__name__)

if PY2:
    import anydbm
else:
    import dbm as anydbm

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

__all__ = ('TrajectoryInfoCache', 'TrajInfo')


class UnknownDBFormatException(KeyError):
    pass


class TrajInfo(object):

    def __init__(self, ndim=0, length=0, offsets=[]):
        self._ndim = ndim
        self._length = length
        self._offsets = offsets

        self._version = 1
        self._hash = -1

    @property
    def version(self):
        return self._version

    @property
    def ndim(self):
        return self._ndim

    @property
    def length(self):
        return self._length

    @property
    def offsets(self):
        return self._offsets

    @offsets.setter
    def offsets(self, value):
        self._offsets = np.asarray(value, dtype=np.int64)

    @property
    def hash(self):
        return self._hash


def create_traj_info(db_val):
    fh = BytesIO(str.encode(db_val))
    try:
        arr = np.load(fh)['data']
        info = TrajInfo()
        header = arr[0]

        version = header['data_format_version']
        info._version = version
        if version == 1:
            info._hash = header['filehash']
            info._ndim = arr[1]
            info._length = arr[2]
            info._offsets = arr[3]
        else:
            raise ValueError("unknown version %s" % version)
        return info
    except Exception as ex:
        raise UnknownDBFormatException(ex)


class TrajectoryInfoCache(object):

    """ stores trajectory lengths associated to a file based hash (mtime, name, 1mb of data)

    Parameters
    ----------
    database_filename : str (optional)
        if given the cache is being made persistent to this file. Otherwise the
        cache is lost after the process has finished.

    Notes
    -----
    Do not instantiate this yourself, but use the instance provided by this
    module.

    """
    _instance = None

    @staticmethod
    def instance():
        if TrajectoryInfoCache._instance is None:
            # singleton pattern
            cfg_dir = conf_values['pyemma']['cfg_dir']
            filename = os.path.join(cfg_dir, "trajlen_cache")
            TrajectoryInfoCache._instance = TrajectoryInfoCache(filename)
        return TrajectoryInfoCache._instance

    def __init__(self, database_filename=None):
        if database_filename is not None:
            self._database = anydbm.open(database_filename, flag="c")
        else:
            self._database = {}

        self._database['db_version'] = '1'
        self._write_protector = Semaphore()

    def __getitem__(self, filename_reader_tuple):
        filename, reader = filename_reader_tuple
        key = self._get_file_hash(filename)
        result = None
        try:
            result = self._database[key]
            info = create_traj_info(result)
        # handle cache misses and not interpreteable results by re-computation.
        # Note: this also handles UnknownDBFormatExceptions!
        except KeyError:
            info = reader._get_traj_info(filename)
            # store info in db
            result = self.__setitem__(filename, info)

        return info

    def __format_value(self, traj_info):
        fh = BytesIO()

        header = {'data_format_version': 1,
                  'filehash': traj_info.hash,  # back reference to file by hash
                  }

        array = np.empty(4, dtype=object)

        array[0] = header
        array[1] = traj_info.ndim
        array[2] = traj_info.length
        array[3] = traj_info.offsets

        np.savez_compressed(fh, data=array)
        fh.seek(0)
        return fh.read()

    def _get_file_hash(self, filename):
        statinfo = os.stat(filename)

        # only remember file name without path, to re-identify it when its
        # moved
        hash_value = hash(os.path.basename(filename))
        hash_value ^= hash(statinfo.st_mtime)
        hash_value ^= hash(statinfo.st_size)

        # now read the first megabyte and hash it
        with open(filename, mode='rb') as fh:
            data = fh.read(1024)

        hash_value ^= hash(data)
        return str(hash_value)

    def __setitem__(self, filename, traj_info):
        dbval = self.__format_value(traj_info)

        self._write_protector.acquire()
        self._database[str(traj_info.hash)] = dbval
        self._write_protector.release()

        return dbval

    def clear(self):
        self._database.clear()
