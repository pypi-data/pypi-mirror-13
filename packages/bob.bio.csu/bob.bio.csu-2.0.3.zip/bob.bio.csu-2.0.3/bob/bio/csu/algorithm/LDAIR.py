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

from .. import utils

class LDAIR (bob.bio.base.algorithm.Algorithm):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRLDA` class to be used as an image :py:class:`bob.bio.base.algorithm.Algorithm`.

  **Parameters:**

  REGION_ARGS : list
    The region arguments as taken from facerec2010.baseline.lda.CohortLDA_REGIONS

  REGION_KEYWORDS : dict
    The region keywords as taken from facerec2010.baseline.lda.CohortLDA_KEYWORDS

  multiple_model_scoring : str
    The scoring strategy if models are enrolled from several images, see :py:func:`bob.bio.base.score_fusion_strategy` for more information.

  multiple_probe_scoring : str
    The scoring strategy if a score is computed from several probe images, see :py:func:`bob.bio.base.score_fusion_strategy` for more information.
  """
  def __init__(
      self,
      REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS,
      REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS,
      multiple_model_scoring = 'max', # by default, compute the maximum score between several models and the probe
      multiple_probe_scoring = 'max'  # by default, compute the maximum score between the model and several probes
  ):
    bob.bio.base.algorithm.Algorithm.__init__(self, multiple_model_scoring=multiple_model_scoring, multiple_probe_scoring=multiple_probe_scoring, **REGION_KEYWORDS)
    self.ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.use_cohort = 'cohort_adjust' not in REGION_ARGS[0] or REGION_ARGS[0]['cohort_adjust']


  def _check_feature(self, feature):
    """Checks that the features are of the desired data type."""
    assert isinstance(feature, facerec2010.baseline.common.FaceRecord)
    assert hasattr(feature, "features")


  def load_projector(self, projector_file):
    """This function loads the Projector from the given projector file.
    This is only required when the cohort adjustment is enabled.

    **Parameters:**

    projector_file : str
      The name of the projector file.
      The file is actually not used, but instead we load the extractor file, which needs to be in the same directory, and must be called "Extractor.hdf5"
    """
    # To avoid re-training the Projector, we load the Extractor file instead.
    # This is only required when the cohort adjustment is enabled, otherwise the default parametrization of LDA-IR should be sufficient.
    # Be careful, THIS IS A HACK and it might not work in all circumstances!
    if self.use_cohort:
      extractor_file = projector_file.replace("Projector", "Extractor")
      self.ldair = utils.load_pickle(extractor_file)


  def enroll(self, enroll_features):
    """enroll(enroll_features) -> model

    Enrolls a model from features from several images by simply storing all given features.

    **Parameters:**

    enroll_features : [:py:class:`facerec2010.baseline.common.FaceRecord`]
      The features used to enroll the model.

    **Returns:**

    model : [:py:class:`facerec2010.baseline.common.FaceRecord`]
      The model, which is identical to the ``enroll_features``.
    """
    [self._check_feature(f) for f in enroll_features]
    # just store all features (should be of type FaceRecord)
    # since the given features are already in the desired format, there is nothing to do.
    return enroll_features


  def write_model(self, model, model_file):
    """Saves the enrolled model to file using the :py:func:`bob.bio.csu.save_pickle` function.

    **Parameters:**

    model : [:py:class:`facerec2010.baseline.common.FaceRecord`]
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

    model : [:py:class:`facerec2010.baseline.common.FaceRecord`]
      The model read from file.
    """
    # just read the model from .pkl file
    return utils.load_pickle(model_file)

  # probe and model are identically stored in a .pkl file
  read_probe = read_model

  def score(self, model, probe):
    """score(model, probe) -> score

    Compute the score for the given model (a list of FaceRecords) and a probe (a FaceRecord).

    **Parameters:**

    model : [:py:class:`facerec2010.baseline.common.FaceRecord`]
      The model to compare, which is actually a list of extracted features.

    probe : :py:class:`facerec2010.baseline.common.FaceRecord`
      The probe to compare.

    **Returns**:

    score : float
      A score that was fused using the fusion function defined in the constructor of this class.
    """
    if isinstance(model, list):
      # compute score fusion strategy with several model features (which is implemented in the base class)
      return self.score_for_multiple_models(model, probe)
    else:
      self._check_feature(model)
      self._check_feature(probe)

      return self.ldair.similarityMatrix([probe], [model])[0,0]
