#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 09:27:59 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pickle
import bob.io.base

def load_pickle(file_like):
  """load_pickle(file_like) -> data

  Loads a file that was written with the :py:func:`save_pickle` function and returns its content.

  **Keyword Parameters**

  file_like: :py:class:`bob.io.base.HDF5File` or :py:class:`str`
    The file containing the data to be read.

  **Returns***

  data : various types
    The data read from the file.
  """
  hdf5 = file_like if isinstance(file_like, bob.io.base.HDF5File) else bob.io.base.HDF5File(file_like)
  return pickle.loads(hdf5.get("Data"))

def save_pickle(data, file_like):
  """save_pickle(data, file_like) -> None

  Saves the given data in the given file using the :py:mod:`pickle` module.

  The data is first pickled into a string, which is written into the given file

  **Keyword Parameters**

  data : various types
    The data write into the file.
    The data type must support pickling.

  file_like: :py:class:`bob.io.base.HDF5File` or :py:class:`str`
    The file or the name of the file to write.
    If ``file_like`` is of type :py:class:`bob.io.base.HDF5File`, it needs to be open for writing.
  """

  hdf5 = file_like if isinstance(file_like, bob.io.base.HDF5File) else bob.io.base.HDF5File(file_like, 'w')
  hdf5.set("Data", pickle.dumps(data))
