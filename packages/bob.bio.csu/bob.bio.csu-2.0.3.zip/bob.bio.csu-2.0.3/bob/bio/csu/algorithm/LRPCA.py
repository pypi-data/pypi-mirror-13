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

import facerec2010
import bob.bio.base
import numpy

from .. import utils


class LRPCA (bob.bio.base.algorithm.Algorithm):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRPCA` class to be used as an image :py:class:`bob.bio.base.algorithm.Algorithm`.

  **Parameters:**

  TUNING : dict
    The tuning for the LRPCA algorithm as taken from the :py:attr:`facerec2010.baseline.lrpca.GBU_TUNING`.

  multiple_model_scoring : str
    The scoring strategy if models are enrolled from several images, see :py:func:`bob.bio.base.score_fusion_strategy` for more information.

  multiple_probe_scoring : str
    The scoring strategy if a score is computed from several probe images, see :py:func:`bob.bio.base.score_fusion_strategy` for more information.
  """

  def __init__(
      self,
      TUNING = facerec2010.baseline.lrpca.GBU_TUNING,
      multiple_model_scoring = 'max', # by default, compute the average between several models and the probe
      multiple_probe_scoring = 'max'  # by default, compute the average between the model and several probes
  ):
    bob.bio.base.algorithm.Algorithm.__init__(self, multiple_model_scoring=multiple_model_scoring, multiple_probe_scoring=multiple_probe_scoring, **TUNING)
    # initialize LRPCA (not sure if this is really required)
    self.lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)


  def _check_feature(self, feature):
    """Assures that the feature is of the desired type"""
    assert isinstance(feature, numpy.ndarray)
    assert feature.ndim == 1
    assert feature.dtype == numpy.float64

  def _check_model(self, model):
    """Assures that the model is of the desired type"""
    assert isinstance(model, facerec2010.baseline.pca.FaceRecord)
    assert hasattr(model, "feature")


  def enroll(self, enroll_features):
    """enroll(enroll_features) -> model

    Enrolls a model from features from several images by simply storing all given features.

    **Parameters:**

    enroll_features : [:py:class:`numpy.ndarray`]
      The features used to enroll the model.

    **Returns:**

    model : [:py:class:`facerec2010.baseline.pca.FaceRecord`]
      The model, which a collection of face records, storing the given ``enroll_features``.
    """
    # no rule to enroll features in the LRPCA setup, so we just store all features
    # create model Face records
    model_records = []
    for feature in enroll_features:
      model_record = facerec2010.baseline.pca.FaceRecord(None,None,None)
      model_record.feature = feature[:]
      model_records.append(model_record)
    return model_records


  def write_model(self, model, model_file):
    """Saves the enrolled model to file using the :py:func:`bob.bio.csu.save_pickle` function.

    **Parameters:**

    model : [:py:class:`facerec2010.baseline.pca.FaceRecord`]
      The model to be written.

    model_file : str
      The name of the model file that is written.
    """
    # just dump the model to .pkl file
    utils.save_pickle(model, model_file)


  def read_model(self, model_file):
    """read_model(model_file) -> model

    Loads an enrolled model from file using the :py:func:`bob.bio.csu.load_pickle` function.

    **Parameters:**

    model_file : str
      The name of the model file to be read.

    **Returns:**

    model : [:py:class:`facerec2010.baseline.pca.FaceRecord`]
      The model read from file.
    """
    # just read the model from .pkl file
    return utils.load_pickle(model_file)


  def score(self, model, probe):
    """score(model, probe) -> score

    Compute the score for the given model (a list of FaceRecords) and a probe (a FaceRecord).

    **Parameters:**

    model : [:py:class:`facerec2010.baseline.pca.FaceRecord`]
      The model to compare, which is actually a list of extracted features.

    probe : :py:class:`numpy.ndarray`
      The probe to compare.

    **Returns**:

    score : float
      A score that was fused using the fusion function defined in the constructor of this class.
    """
    if isinstance(model, list):
      # compute score fusion strategy with several model features (which is implemented in the base class)
      return self.score_for_multiple_models(model, probe)
    else:
      self._check_model(model)
      self._check_feature(probe)
      # compute score for one model and one probe
      probe_record = facerec2010.baseline.pca.FaceRecord(None,None,None)
      probe_record.feature = probe

      return self.lrpca.similarityMatrix([probe_record], [model])[0,0]
