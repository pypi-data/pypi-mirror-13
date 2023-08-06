#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
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


import unittest
import os
import numpy

from nose.plugins.skip import SkipTest

import pkg_resources

regenerate_refs = False

import bob.bio.base
import bob.bio.face

from bob.bio.face.test.test_preprocessors import _annotation, _compare


def _image(preprocessor):
  return preprocessor.read_original_data(pkg_resources.resource_filename('bob.bio.face.test', 'data/testimage.jpg'))


def test_lrpca():
  # load resource
  preprocessor = bob.bio.base.load_resource('lrpca', 'preprocessor')
  assert isinstance(preprocessor, bob.bio.csu.preprocessor.LRPCA)
  assert isinstance(preprocessor, bob.bio.base.preprocessor.Preprocessor)

  # read input
  image, annotation = _image(preprocessor), _annotation()

  # execute face cropper
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_preprocessed.hdf5')
  # for some reason, LR-PCA produces slightly different outputs on some machines
  _compare(preprocessor(image, annotation), reference, preprocessor.write_data, preprocessor.read_data, atol=1., rtol=1e-2)

def test_lrpca_detect():
  # create preprocessor including face detector
  preprocessor = bob.bio.csu.preprocessor.LRPCA(face_detector='landmark-detect')

  # read input
  image, annotation = _image(preprocessor), _annotation()

  # execute face cropper
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_detected.hdf5')
  # for some reason, LR-PCA produces slightly different outputs on some machines
  _compare(preprocessor(image, annotation), reference, preprocessor.write_data, preprocessor.read_data, atol=1., rtol=1e-2)



def test_ldair():
  # load resource
  preprocessor = bob.bio.base.load_resource('lda-ir', 'preprocessor')
  assert isinstance(preprocessor, bob.bio.csu.preprocessor.LDAIR)
  assert isinstance(preprocessor, bob.bio.base.preprocessor.Preprocessor)

  # read input
  image, annotation = _image(preprocessor), _annotation()

  # execute face cropper
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_preprocessed.hdf5')
  _compare(preprocessor(image, annotation), reference, preprocessor.write_data, preprocessor.read_data, atol=1.)

def test_ldair_detect():
  # create preprocessor including face detector
  preprocessor = bob.bio.csu.preprocessor.LDAIR(face_detector='landmark-detect')

  # read input
  image, annotation = _image(preprocessor), _annotation()

  # execute face cropper
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_detected.hdf5')
  # for some reason, LR-PCA produces slightly different outputs on some machines
  _compare(preprocessor(image, annotation), reference, preprocessor.write_data, preprocessor.read_data, atol=1., rtol=1e-2)
