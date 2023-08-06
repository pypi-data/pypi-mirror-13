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

from .. import utils

import logging
logger = logging.getLogger("bob.bio.csu")

class LRPCA (bob.bio.base.extractor.Extractor):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRPCA` class to be used as an image :py:class:`bob.bio.base.extractor.Extractor`.

  **Parameters:**

  TUNING : dict
    The tuning for the LRPCA algorithm as taken from the :py:attr:`facerec2010.baseline.lrpca.GBU_TUNING`.
  """

  def __init__(self, TUNING = facerec2010.baseline.lrpca.GBU_TUNING):
    bob.bio.base.extractor.Extractor.__init__(self, requires_training=True, split_training_data_by_client=True, **TUNING)
    self.lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)


  def _check_image(self, image):
    assert isinstance(image, numpy.ndarray)
    assert image.ndim == 2

  def _py_image(self, image):
    """Converts the given image to pyvision images."""
    self._check_image(image)
    pil_image = PIL.Image.new("L",(image.shape[1],image.shape[0]))
    # TODO: Test if there is any faster method to convert the image type
    for y in range(image.shape[0]):
      for x in range(image.shape[1]):
        # copy image content (re-order [y,x] to (x,y))
        pil_image.putpixel((x,y),image[y,x])

    # convert to pyvision image
    py_image = pyvision.Image(pil_image)
    return py_image


  def train(self, training_images, extractor_file):
    """Trains the LRPCA module with the given image list.

    The resulting object will be saved into the given ``extractor_file`` using the :py:func:`bob.bio.csu.save_pickle` function.

    **Parameters:**

    training_images : [[numpy.ndarray]]
      The list of training images, which is split into images of the same clients.

    extractor_file : str
      The file to write into.
    """
    train_count = 0
    for client_index, client_images in enumerate(training_images):
      for image in client_images:

        # convert the image into a data type that is understood by FaceRec2010
        pyimage = self._py_image(image)

        # append training data to the LRPCA training
        # (the None parameters are due to the fact that preprocessing happened before)
        self.lrpca.addTraining(str(client_index), pyimage, None, None, None),

        train_count += 1

    logger.info("  -> Training LRPCA with %d images", train_count)
    self.lrpca.train()

    # and write the result to file, which in this case simply used pickle
    utils.save_pickle(self.lrpca, extractor_file)


  def load(self, extractor_file):
    """Loads the trained LRPCA feature extractor from the given ``extractor_file`` using the :py:func:`bob.bio.csu.load_pickle` function.

    **Parameters:**


    extractor_file : str
      The file to be read, which has been written by the :py:meth:`train` function.
    """
    # read LRPCA projector
    self.lrpca = utils.load_pickle(extractor_file)


  def __call__(self, image):
    """__call__(image) -> extracted

    Extracts image features using LRPCA.
    The returned value is just the :py:attr:`facerec2010.baseline.common.FaceRecord.feature` array.

    **Parameters:**

    image : 2D :py:class:`numpy.ndarray`
      The color image to project.

    **Returns:**

    extracted : :py:class:`numpy.ndarray`
      The extracted image feature.
    """
    # create pvimage
    pyimage = self._py_image(image)
    # Projects the data by creating a "FaceRecord"
    face_record = self.lrpca.getFaceRecord(pyimage, None, None, None)
    # return the projected data, which is stored as a numpy.ndarray
    return face_record.feature
