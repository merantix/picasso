========
Settings
========

Application settings are `managed by Flask`_.  This means you can use
environment variables or a configuration file.

To specify your own configuration, use the ``PICASSO_SETTINGS``
environment variable.  Let's look at the Tensorflow MNIST example.

.. code-block:: bash

   export PICASSO_SETTINGS=/absolute/path/to/repo/picasso/picasso/examples/tensorflow/config.py

Tells the app to use this configuration instead of the default one.  Inside
``config.py``, we have:

.. code-block:: python3

   import os
   
   base_dir = os.path.split(os.path.abspath(__file__))[0]
   
   BACKEND_ML = 'tensorflow'
   BACKEND_PREPROCESSOR_NAME = 'util'
   BACKEND_PREPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
   BACKEND_POSTPROCESSOR_NAME = 'postprocess'
   BACKEND_POSTPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
   BACKEND_PROB_DECODER_NAME = 'prob_decode'
   BACKEND_PROB_DECODER_PATH = os.path.join(base_dir, 'util.py')
   DATA_DIR = os.path.join(base_dir, 'data-volume')

Any lowercase line is ignored for the purposes of determining a setting.  These
can also be set via environment variables, but you must append the app name.
For instance ``BACKEND_ML = 'tensorflow'`` would become ``export
PICASSO_BACKEND_ML=tensorflow``.

For explanations of each setting, see :mod:`picasso.settings`.  Any
additional settings starting with `BACKEND_` will be sent to the model backend
as a keyword argument.  The input and output tensor names can be passed to the
Tensorflow backend in this way:

.. code-block:: python3

   ...
   BACKEND_TF_PREDICT_VAR='Softmax:0'
   BACKEND_TF_INPUT_VAR='convolution2d_input_1:0'

.. _managed by Flask: http://flask.pocoo.org/docs/latest/config/
