.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Mon Nov 10 18:45:01 CET 2014

.. _bob.bio.csu.installation:

============
Installation
============

The current package is just a set of wrapper classes for the CSU ``facerec2010`` module, which is contained in the `CSU Face Recognition Resources`_, where you need to download the Baseline 2011 Algorithms.


Patching the CSU Face Recognition Resources
-------------------------------------------

To be compatible with ``bob.bio``, the CSU toolkit needs to be patched.
If you haven't patched it yet, please follow the set of instructions:

1. Download the ``bob.bio.csu`` package from our `PyPI page <http://pypi.python.org/pypi/bob.bio.csu>`_ and extract it into a directory of your choice.

2. Generate the binaries of this package without the CSU toolkit.
   We provide a special buildout configuration file for that:

   .. code-block:: sh

      $ python bootstrap-buildout.py
      $ ./bin/buildout -c buildout-before-patch.cfg

   This will disable the CSU code for a while.


3. Patch the CSU toolkit by calling:

   .. code-block:: sh

      $ ./bin/patch_CSU.py [PATH_TO_YOUR_CSU_COPY]

   If you get any error message, the sources of the CSU might have changed (the latest test was done in December 2012).
   Please file a bug report in `our GitHub page <http://www.github.com/bioidiap/xfacereclib.extension.CSU>`_ to inform us so that we can provide a new patch.


4. Update the CSU toolkit path in the *buildout.cfg* file by setting the ``csu-dir`` variable via replacing the ``[PATH_TO_YOUR_CSU_COPY]`` with your actual directory:

  .. code-block:: py

     csu-dir = /path/to/your/csu/copy

  and re-generate the binaries, this time including the CSU toolkit::

  .. code-block:: sh

     $ bin/buildout

  *or* simply re-generate the binaries with the option:

  .. code-block:: sh

     $ bin/buildout buildout:csu-dir=/path/to/your/csu/copy


.. note::
   When you are working at Idiap, you might get a pre-patched version of the CSU Face Recognition Resources.

.. warning::
   After patching the CSU toolkit, the original experiments of the CSU toolkit will not work any more!
   Maybe it is a good idea to make a save-copy of your CSU copy before applying the patch.


Verifying your Installation
---------------------------
After the CSU toolkit is patched, please verify that the installation works as expected.
For this, please run our test environment by calling:

.. code-block:: sh

   $ bin/nosetests -vs

Please assure that all 6 tests pass.


Running CSU experiments with ``bob.bio``
----------------------------------------
The easiest way to run any experiment with the CSU tools is to use ``bob.bio`` directly, using any of the :ref:`databases from bob.bio.face <bob.bio.face.databases>`.
After running the command lines above, the CSU tools should be registered as :ref:`Resources <bob.bio.base.resources>`, i.e., they are listed in the:

.. code-block:: sh

  $ ./bin/resources.py

and can be used on as a command line parameter like:

.. code-block:: sh

  $ ./bin/verify.py --preprocessor lda-ir --extractor lda-ir --algorithm lda-ir --database gbu ...

Additionally, now two new baseline experiments ``lrpca`` and ``lda-ir`` can be run in using the ``./bin/baselines.py`` script, see :ref:`bob.bio.face.baselines`.

Please check the `bob.bio Documentation <bob.bio.base.experiments>`_ on more details on how to run face recognition experiments using the above mentioned two scripts.


One example on how to compare the CSU algorithms to other state-of-the-art algorithms using the FaceRecLib_ (on the base of which ``bob.bio`` is originally build) is given in our paper:

.. code-block:: latex

  @inproceedings{Guenther_BeFIT2012,
         author = {G{\"u}nther, Manuel AND Wallace, Roy AND Marcel, S{\'e}bastien},
         editor = {Fusiello, Andrea AND Murino, Vittorio AND Cucchiara, Rita},
       keywords = {Biometrics, Face Recognition, Open Source, Reproducible Research},
          month = oct,
          title = {An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms},
      booktitle = {Computer Vision - ECCV 2012. Workshops and Demonstrations},
         series = {Lecture Notes in Computer Science},
         volume = {7585},
           year = {2012},
          pages = {547-556},
      publisher = {Springer Berlin},
       location = {Heidelberg},
            url = {http://publications.idiap.ch/downloads/papers/2012/Gunther_BEFIT2012_2012.pdf}
  }

The source code for this paper, which actually uses the FaceRecLib_, can be found under http://pypi.python.org/pypi/xfacereclib.paper.BeFIT2012.

.. note::
   The source code for http://pypi.python.org/pypi/xfacereclib.paper.BeFIT2012 depends on an older version of Bob and an old version of this package, and is not (yet) ported to the new Bob version 2.0.

.. include:: links.rst
