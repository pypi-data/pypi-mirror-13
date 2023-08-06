#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Oct 29 10:12:23 CET 2012
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

from .test_extractors import _compare_lda_face_records

def _compare_pca_face_records(f1, f2):
  assert isinstance(f1, facerec2010.baseline.pca.FaceRecord)
  assert isinstance(f2, facerec2010.baseline.pca.FaceRecord)
  assert hasattr(f1, "feature")
  assert hasattr(f2, "feature")
  assert numpy.allclose(f1.feature, f2.feature, atol=1e-3, rtol=1e-8)

def test_lrpca():
  # read feature using the extractor
  extractor = bob.bio.base.load_resource('lrpca', 'extractor')
  feature_file = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_extracted.hdf5')
  extracted = extractor.read_feature(feature_file)

  # load resource
  algorithm = bob.bio.base.load_resource('lrpca', 'algorithm')

  # enroll model
  model = algorithm.enroll([extracted])
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/lrpca_model.hdf5')
  if regenerate_refs:
    algorithm.write_model(model, reference)

  # TODO: compare reference model with new one
  reference = algorithm.read_model(reference)
  [_compare_pca_face_records(m, r) for m,r in zip(model,reference)]

  # Read probe; should be identical to the feature
  probe = algorithm.read_probe(feature_file)
  assert numpy.allclose(extracted, probe)

  # score
  sim = algorithm.score(model, probe)
  # LRPCA by default computes the correlation between model and probe, which is 1 in this case
  # weirdly, the similarity is not exactly one for some reason...
  assert abs(sim - 1.) < 1e-4


def test_ldair():
  # read feature using the extractor
  extractor = bob.bio.base.load_resource('lda-ir', 'extractor')
  feature_file = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_extracted.hdf5')
  extracted = extractor.read_feature(feature_file)

  # load resource
  algorithm = bob.bio.base.load_resource('lda-ir', 'algorithm')

  # enroll model
  model = algorithm.enroll([extracted])
  reference = pkg_resources.resource_filename('bob.bio.csu.test', 'data/ldair_model.hdf5')
  if regenerate_refs:
    algorithm.write_model(model, reference)

  # TODO: compare reference model with new one
  reference = algorithm.read_model(reference)
  [_compare_lda_face_records(m, r) for m,r in zip(model,reference)]

  # Read probe; should be identical to the feature
  probe = algorithm.read_probe(feature_file)
  _compare_lda_face_records(extracted, probe)

  # score
  sim = algorithm.score(model, probe)
  # LDA-IR by default returns the negative L2 distance, which is 0 in this case
  assert abs(sim) < 1e-5
