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
import pyvision
import PIL
import numpy
import bob.bio.base

import logging
logger = logging.getLogger("bob.bio.csu")

from .. import utils

class LDAIR (bob.bio.base.extractor.Extractor):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRLDA` class to be used as an image :py:class:`bob.bio.base.extractor.Extractor`.

  **Parameters:**

  REGION_ARGS : list
    The region arguments as taken from :py:attr:`facerec2010.baseline.lda.CohortLDA_REGIONS`.

  REGION_KEYWORDS : dict
    The region keywords as taken from :py:attr:`facerec2010.baseline.lda.CohortLDA_KEYWORDS`.
  """
  def __init__(self, REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS, REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS):
    bob.bio.base.extractor.Extractor.__init__(self, requires_training=True, split_training_data_by_client=True, **REGION_KEYWORDS)
    self.ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.layers = len(REGION_ARGS)
    self.use_cohort = 'cohort_adjust' not in REGION_ARGS[0] or REGION_ARGS[0]['cohort_adjust']

    # overwrite the training image list generation from the file selector
    # since LRPCA needs training data to be split up into identities
    self.use_training_images_sorted_by_identity = True


  def _check_image(self, image):
    """Checks that the input data is in the expected format"""
    assert isinstance(image, numpy.ndarray)
    assert image.ndim == 3
    assert image.dtype == numpy.uint8

  def _py_image(self, image):
    """Generates a 4D structure used for LDA-IR feature extraction"""

    pil_image = PIL.Image.new("RGB",(image.shape[2], image.shape[1]))
    # TODO: Test if there is any faster method to convert the image type
    for y in range(image.shape[1]):
      for x in range(image.shape[2]):
        # copy image content (re-order [y,x] to (x,y) and add the colors as (r,g,b))
        pil_image.putpixel((x,y),(image[0,y,x], image[1,y,x], image[2,y,x]))

    # convert to pyvision image
    py_image = pyvision.Image(pil_image)
    # generate some copies of the image
    return [py_image.copy() for i in range(self.layers)]


  def train(self, training_images, extractor_file):
    """Trains the LDA-IR module with the given image list.

    The resulting object will be saved into the given ``extractor_file`` using the :py:func:`bob.bio.csu.save_pickle` function.

    **Parameters:**

    training_images : [[numpy.ndarray]]
      The list of training images, which is split into images of the same clients.

    extractor_file : str
      The file to write into.
    """
    [self._check_image(image) for client_images in training_images for image in client_images]
    train_count = 0
    for client_index, client_images in enumerate(training_images):
      # Initializes an arrayset for the data
      for image in client_images:
        # create PIL image (since there are differences in the
        # implementation of pyvision according to different image types)
        # Additionally, PIL used pixels in (x,y) order
        pyimage = self._py_image(image)

        # append training data to the LDA-IR training
        # (the None parameters are due to the fact that preprocessing happened before)
        self.ldair.addTraining(str(client_index), pyimage, None, None, None)

        train_count += 1

    logger.info("  -> Training LDA-IR with %d images", train_count)
    self.ldair.train()

    if self.use_cohort:
      logger.info("  -> Adding cohort images")
      # add image cohort for score normalization
      for client_images in training_images:
        # Initializes an arrayset for the data
        for image in client_images:
          pyimage = self._py_image(image)
          self.ldair.addCohort(pyimage, None, None, None)


    # and write the result to file, which in this case simply used pickle
    utils.save_pickle(self.ldair, extractor_file)


  def load(self, extractor_file):
    """Loads the LDA-IR from the given extractor file using the :py:func:`bob.bio.csu.load_pickle` function.

    **Parameters:**


    extractor_file : str
      The file to be read, which has been written by the :py:meth:`train` function.
    """
    # read LDA-IR extractor
    self.ldair = utils.load_pickle(extractor_file)


  def __call__(self, image):
    """__call__(image) -> extracted

    Extracts image features using LDA-IR.

    **Parameters:**

    image : 3D :py:class:`numpy.ndarray`
      The color image to project.

    **Returns:**

    extracted : :py:class:`facerec2010.baseline.common.FaceRecord`
      The extracted image feature.
    """
    self._check_image(image)
    # create pvimage
    pyimage = self._py_image(image)
    # Projects the data (by creating a "Face Record"
    face_record = self.ldair.getFaceRecord(pyimage, None, None, None, compute_cohort_scores = self.use_cohort)

    return face_record


  def write_feature(self, feature, feature_file):
    """Saves the extracted LDA-IR feature to file using :py:func:`bob.bio.csu.save_pickle`.

    **Parameters:**

    feature : :py:class:`facerec2010.baseline.common.FaceRecord`
      The extracted feature to be written.

    feature_file : str or :py:class:`bob.io.base.HDF5File`
      The name of the file, or the file opened for writing.
    """
    # write the feature to a .pkl file
    # (since FaceRecord does not have a save method)
    utils.save_pickle(feature, feature_file)


  def read_feature(self, feature_file):
    """read_feature(feature_file) -> feature

    Reads the extracted LDA-IR feature from file using :py:func:`bob.bio.csu.load_pickle`.

    **Parameters:**

    feature_file : str or :py:class:`bob.io.base.HDF5File`
      The name of the file, or the file opened for reading.

    **Returns:**

    feature : :py:class:`facerec2010.baseline.common.FaceRecord`
      The read feature.
    """
    # read the feature from .pkl file
    return utils.load_pickle(feature_file)
