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
import bob.bio.face

class LRPCA (bob.bio.face.preprocessor.FaceCrop):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRPCA` class to be used as an image :py:class:`bob.bio.base.preprocessor.Preprocessor`.

  **Parameters:**

  ``TUNING`` : {}
    The tuning for the LRPCA algorithm as taken from the :py:attr:`facerec2010.baseline.lrpca.GBU_TUNING`.

  ``face_detector`` : :py:class:`bob.bio.face.preprocessor.FaceDetect` or str
    The face detector to be used to detect the detected face.
    Might be an instance of a :py:class:`FaceDetect` or the name of a face detector resource.
  """

  def __init__(self, TUNING = facerec2010.baseline.lrpca.GBU_TUNING, face_detector = None):
    bob.bio.base.preprocessor.Preprocessor.__init__(self, TUNING=str(TUNING), face_detector=str(face_detector))
    self.lrpca = facerec2010.baseline.lrpca.LRPCA(**TUNING)
    self.face_detector = bob.bio.face.preprocessor.utils.load_cropper(face_detector)

    if self.face_detector is not None:
      assert isinstance(self.face_detector, bob.bio.face.preprocessor.FaceDetect)
      # asign ourself to be the face cropper that should be used after face detection
      self.face_detector.cropper = self

  def _py_image(self, image):
    """Converts the given image to pyvision images."""
    pil_image = PIL.Image.new("L",(image.shape[1],image.shape[0]))
    # TODO: Test if there is any faster method to convert the image type
    for y in range(image.shape[0]):
      for x in range(image.shape[1]):
        # copy image content (re-order [y,x] to (x,y))
        pil_image.putpixel((x,y),image[y,x])

    # convert to pyvision image
    py_image = pyvision.Image(pil_image)
    return py_image


  def crop_face(self, image, annotations):
    """__call__(image, annotations) -> preprocessed
    Preprocesses the image using the :py:meth:`facerec2010.baseline.lrpca.LRPCA.preprocess` function.

    **Parameters:**

    image : :py:class:`pyvision.Image` or :py:class:`numpy.ndarray`
      The gray level or color image that should be preprocessed.

    annotations : dict
      The eye annotations for the image.
      They need to be specified as ``{'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}``, where right and left is in subject perspective.

    **Returns:**

    preprocessed : numpy.ndarray
      The preprocessed image, in default Bob format.
    """
    assert isinstance(image, (pyvision.Image, numpy.ndarray))
    if isinstance(image, numpy.ndarray):
      image = self._py_image(image)

    # assure that the eye positions are in the set of annotations
    if annotations is None or 'leye' not in annotations or 'reye' not in annotations:
      raise ValueError("The LRPCA image cropping needs eye positions, but they are not given.")

    # Warning! Left and right eye are mixed up here!
    # The lrpca preprocess expects left_eye_x < right_eye_x
    tile = self.lrpca.preprocess(
        image,
        rect=None,
        leye = pyvision.Point(annotations['reye'][1], annotations['reye'][0]),
        reye = pyvision.Point(annotations['leye'][1], annotations['leye'][0])
    )

    # pyvision used images in (x,y)-order.
    # To be consistent to the (y,x)-order in Bob, we have to transpose
    return tile.asMatrix2D().transpose()


  def __call__(self, image, annotations):
    """__call__(image, annotations) -> preprocessed
    Preprocesses the image using the :py:meth:`facerec2010.baseline.lrpca.LRPCA.preprocess` function.

    **Parameters:**

    image : :py:class:`pyvision.Image` or :py:class:`numpy.ndarray`
      The gray level or color image that should be preprocessed.

    annotations : dict
      The eye annotations for the image.
      They need to be specified as ``{'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}``, where right and left is in subject perspective.

    **Returns:**

    preprocessed : numpy.ndarray
      The preprocessed image, in default Bob format.
    """
    if self.face_detector is not None:
      if isinstance(image, pyvision.Image):
        # the face detector requires numpy arrays
        image = image.asMatrix2D().transpose().astype(numpy.float64)
      # call face detector with the (tansformed) image
      return self.face_detector.crop_face(image, annotations)

    return self.crop_face(image, annotations)



  def read_original_data(self, image_file):
    """read_original_data(image_file) -> image

    Reads the original images using functionality from pyvision.

    **Parameters:**

    image_file : str
      The image file to be read, can contain a gray level or a color image.

    **Returns:**

    image : :py:class:`pyvision.Image`
      The image read from file.
    """
    # we use pyvision to read the images. Hence, we don't have to struggle with conversion here
    return pyvision.Image(str(image_file))
