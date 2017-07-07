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
   
   MODEL_CLS_PATH = os.path.join(base_dir, 'model.py')
   MODEL_CLS_NAME = 'TensorflowMNISTModel'
   MODEL_LOAD_ARGS = {
       'data_dir': os.path.join(base_dir, 'data-volume'),
       'tf_input_var': 'convolution2d_input_1:0',
       'tf_predict_var': 'Softmax:0',
   }

Any lowercase line is ignored for the purposes of determining a setting.
``MODEL_LOAD_ARGS`` will pass the arguments along to the model's ``load`` 
function.

For explanations of each setting, see :mod:`picasso.config`.  

.. _managed by Flask: http://flask.pocoo.org/docs/latest/config/
