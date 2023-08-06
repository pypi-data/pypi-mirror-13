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
import numpy
import bob.bio.base
import bob.bio.face

class LDAIR (bob.bio.face.preprocessor.FaceCrop):
  """This class defines a wrapper for the :py:class:`facerec2010.baseline.lda.LRLDA` class to be used as an image :py:class:`bob.bio.base.preprocessor.Preprocessor`.

  **Parameters:**

  ``REGION_ARGS`` : []
    The region arguments as taken from :py:attr:`facerec2010.baseline.lda.CohortLDA_REGIONS`.

  ``REGION_KEYWORDS`` : {}
    The region keywords as taken from :py:attr:`facerec2010.baseline.lda.CohortLDA_KEYWORDS`.

  ``face_detector`` : :py:class:`bob.bio.face.preprocessor.FaceDetect` or str
    The face detector to be used to detect the detected face.
    Might be an instance of a :py:class:`FaceDetect` or the name of a face detector resource.
  """

  def __init__(self, REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS, REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS, face_detector = None):
    bob.bio.base.preprocessor.Preprocessor.__init__(self, REGION_ARGS=str(REGION_ARGS), REGION_KEYWORDS=str(REGION_KEYWORDS), face_detector=str(face_detector))
    self.ldair = facerec2010.baseline.lda.LRLDA(REGION_ARGS, **REGION_KEYWORDS)
    self.layers = len(REGION_ARGS)
    self.face_detector = bob.bio.face.preprocessor.utils.load_cropper(face_detector)

    if self.face_detector is not None:
      assert isinstance(self.face_detector, bob.bio.face.preprocessor.FaceDetect)
      # asign ourself to be the face cropper that should be used after face detection
      self.face_detector.cropper = self


  def _numpy_image(self, image):
    """Converts the givne image into a numpy color image in Bob format"""
    np_image = image.asMatrix3D()
    bob_image = numpy.ndarray((np_image.shape[0], np_image.shape[2], np_image.shape[1]), dtype = numpy.uint8)

    # iterate over color layers
    for j in range(np_image.shape[0]):
      bob_image[j,:,:] = np_image[j].transpose()[:,:]
    return bob_image


  def crop_face(self, image, annotations):
    """crop_face(image, annotations = None) -> face

    Executes the face cropping on the given image and returns the cropped version of it.

    **Parameters:**

    ``image`` : 3D :py:class:`numpy.ndarray`
      The face image to be processed.

    ``annotations`` : dict
      The eye annotations for the image.
      They need to be specified as ``{'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}``, where right and left is in subject perspective.

    **Returns:**

    face : 3D :py:class:`numpy.ndarray`
      The cropped face.
    """
    # assure that the eye positions are in the set of annotations
    if annotations is None or 'leye' not in annotations or 'reye' not in annotations:
      raise ValueError("The LDA-IR image cropping needs eye positions, but they are not given.")

    if isinstance(image, numpy.ndarray):
      if len(image.shape) != 3:
        raise ValueError("The LDA-IR image cropping needs color images.")
      image = pyvision.Image(numpy.transpose(image, (0, 2, 1)).astype(numpy.float64))

    assert isinstance(image, pyvision.Image)

    # Warning! Left and right eye are mixed up here!
    # The ldair preprocess expects left_eye_x < right_eye_x
    tiles = self.ldair.preprocess(
        image,
        leye = pyvision.Point(annotations['reye'][1], annotations['reye'][0]),
        reye = pyvision.Point(annotations['leye'][1], annotations['leye'][0])
    )

    # LDAIR preprocessing spits out 4D structure, i.e., [Matrix]
    # with each element of the outer list being identical
    # so we just have to copy the first image

    assert len(tiles) == self.layers
    assert (tiles[0].asMatrix3D() == tiles[1].asMatrix3D()).all()

    # return the image in the format that Bob knows and understands
    return self._numpy_image(tiles[0])


  def __call__(self, image, annotations):
    """Preprocesses the image using the LDA-IR preprocessor :py:meth:`facerec2010.baseline.lda.LRLDA.preprocess`.

    **Parameters:**

    image : :py:class:`pyvision.Image` or :py:class:`numpy.ndarray`
      The color image that should be preprocessed.

    annotations : dict
      The eye annotations for the image.
      They need to be specified as ``{'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}``, where right and left is in subject perspective.

    **Returns:**

    preprocessed : 3D numpy.ndarray
      The preprocessed color image, in default Bob format.
    """
    if self.face_detector is not None:
      if isinstance(image, pyvision.Image):
        # the face detector requires numpy arrays
        image = self._numpy_image(image)
        import bob.io.base
        import bob.io.image
        bob.io.base.save(image.astype(numpy.uint8), "test.png")
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
