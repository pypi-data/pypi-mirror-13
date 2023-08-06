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


import os
import numpy

import pkg_resources

regenerate_refs = False

import bob.bio.base
import bob.bio.face
import facerec2010
import bob.io.base.test_utils
import shutil

from bob.bio.face.test.test_extractors import _compare

def _random_training_set(shape, count = 50, minimum = 0, maximum = 1, as_int = False, seed = 42):
  # generate a random sequence of features
  if seed is not None:
    numpy.random.seed(seed)
  train_set = [numpy.random.random(shape) * (maximum - minimum) + minimum for i in range(count)]
  if as_int:
    train_set = [f.astype(numpy.uint8) for f in train_set]
  return train_set

def _random_training_set_by_id(shape, count = 7, minimum = 0, maximum = 1, as_int = False, seed = 42):
  # generate a random sequence of features
  numpy.random.seed(seed)
  return [_random_training_set(shape, count, minimum, maximum, as_int, seed = None) for i in range(count)]

def _compare_lda_face_records(f1, f2):
  assert isinstance(f1, facerec2010.baseline.common.FaceRecord)
  assert isinstance(f2, facerec2010.baseline.common.FaceRecord)
  assert hasattr(f1, "features")
  assert hasattr(f2, "features")
  assert all([numpy.allclose(a1.feature, a2.feature, atol=1e-5, rtol=1e-8) for a1, a2 in zip(f1.features, f2.features)])


def test_lrpca():
  temp_file = bob.io.base.test_utils.temporary_filename()
  # load resource
  extractor = bob.bio.base.load_resource('lrpca', 'extractor')
  assert isinstance(extractor, bob.bio.csu.extractor.LRPCA)
  assert isinstance(extractor, bob.bio.base.extractor.Extractor)
  assert extractor.requires_training
  assert extractor.split_training_data_by_client

  # read input
  preprocessor = bob.bio.base.load_resource('lrpca', 'preprocessor')
  preprocessed = preprocessor.read_data(pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_preprocessed.hdf5'))

  # for testing purposes, we use a smaller number of kept dimensions
  TUNING = facerec2010.baseline.lrpca.GBU_TUNING
  TUNING['fisher_thresh'] = 20
  extractor2 = bob.bio.csu.extractor.LRPCA(TUNING)

  # we have to train the extractor, so we generate some data
  train_data = _random_training_set_by_id(preprocessed.shape, 10, 0, 255, True)
  reference_file = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_extractor.hdf5')
  try:
    # train extractor
    extractor2.train(train_data, temp_file)

    if regenerate_refs: shutil.copy(temp_file, reference_file)

    # load extractor
    extractor3 = bob.bio.csu.extractor.LRPCA(TUNING)
    extractor3.load(temp_file)
    extractor2.load(reference_file)

    assert numpy.allclose(extractor3(preprocessed), extractor2(preprocessed), atol=1e-3, rtol=1e-5)

  finally:
    if os.path.exists(temp_file):
      os.remove(temp_file)

  # now, we can execute the extractor and check that the feature is still identical
  extracted = extractor3(preprocessed)
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_extracted.hdf5')
  _compare(extracted, reference, extractor.write_feature, extractor.read_feature, atol=1e-3, rtol=1e-5)



def test_ldair():
  temp_file = bob.io.base.test_utils.temporary_filename()
  # load resource
  extractor = bob.bio.base.load_resource('lda-ir', 'extractor')
  assert isinstance(extractor, bob.bio.csu.extractor.LDAIR)
  assert isinstance(extractor, bob.bio.base.extractor.Extractor)
  assert extractor.requires_training
  assert extractor.split_training_data_by_client

  # read input
  preprocessor = bob.bio.base.load_resource('lda-ir', 'preprocessor')
  preprocessed = preprocessor.read_data(pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_preprocessed.hdf5'))

  # we have to train the extractor, so we generate some data
  train_data = _random_training_set_by_id(preprocessed.shape, 10, 0, 255, True)
  reference_file = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_extractor.hdf5')
  try:
    # train extractor
    extractor.train(train_data, temp_file)

    if regenerate_refs: shutil.copy(temp_file, reference_file)

    # load extractor
    extractor2 = bob.bio.csu.extractor.LDAIR(facerec2010.baseline.lda.CohortLDA_REGIONS, facerec2010.baseline.lda.CohortLDA_KEYWORDS)
    extractor2.load(temp_file)
    extractor.load(reference_file)

    # compare extracted features
    _compare_lda_face_records(extractor2(preprocessed), extractor(preprocessed))

  finally:
    if os.path.exists(temp_file):
      os.remove(temp_file)

  # now, we can execute the extractor and check that the feature is still identical
  extracted = extractor2(preprocessed)
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_extracted.hdf5')
  # write reference?
  if regenerate_refs:
    extractor.write_feature(extracted, reference)

  # compare reference
  reference = extractor.read_feature(reference)
  _compare_lda_face_records(extracted, reference)
