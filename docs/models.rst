===============================
Using your own models
===============================

We include three `examples`_ for you to try: a model trained on the `MNIST`_ dataset for both Keras and Tensorflow, and a Keras `VGG16`_ model.  We've tried to make it as simple as possible, but we do make a few assumptions:

#. Your graph has a definitive entry and exit point.  Specifically, a placeholder tensor for some kind of input and output operation (typically image arrays and class probabilities, respectively).

#. These placeholders are of unspecified length.

#. The portion of the computational graph you're interested in requires no other inputs.

If you built your model with Keras using a `Sequential`_ model, you should be more or less good to go.  If you used Tensorflow, you'll need to manually specify the entry and exit points [#]_.

You can specify the backend (Tensorflow or Keras) using the ``PICASSO_BACKEND_ML`` setting. The allowed values are ``tensorflow`` or ``keras`` (see :doc:`settings`).

Your model data
===============

You can specify the data directory with the ``PICASSO_DATA_DIR`` setting. This directory should contain the Keras or Tensorflow checkpoint files.  If multiple checkpoints are found, the latest one will be used (see example `Keras model code`_).

Utility functions
=================

In addition to the graph and weight information of the model itself, you'll need to define a few functions to help the visualization interact with user input, and interpret raw output from your computational graph.  These are arbitrary python functions, and their locations can be specified in the :doc:`settings`.

We'll draw from the `Keras MNIST example`_ for this guide.

Preprocessor
------------

The preprocessor takes images uploaded to the webapp and converts them into arrays that can be used as inputs to your model. The Flask app will haved converted them to `PIL Image`_ objects.

.. code-block:: python3

   MNIST_DIM = (28, 28)

   def preprocess(targets):
       image_arrays = []
       for target in targets:
           im = target.convert('L')
           im = im.resize(MNIST_DIM, Image.ANTIALIAS)
           arr = np.array(im)
           image_arrays.append(arr)

       all_targets = np.array(image_arrays)
       return all_targets.reshape(len(all_targets),
                                  MNIST_DIM[0],
                                  MNIST_DIM[1], 1).astype('float32') / 255

Specifically, we have to convert an arbitrary input color image to a float array of the input size specified with ``MNIST_DIM``.

Postprocessor
-------------

For some visualizations, it's useful to convert a flat representation back into an array with the same shape as the original image.

.. code-block:: python3

   def postprocess(output_arr):
       images = []
       for row in output_arr:
           im_array = row.reshape(MNIST_DIM)
           images.append(im_array)

       return images

This therefore takes an arbitrary array (with the same number of total entries as the image array) and reshapes it back.

Class Decoder
-------------

Class probabilities are usually returned in an array.  For any visualization where we use classification, it's much nicer to have the class labels available.  This method simply attaches the labels to computed probabilities.

.. code-block:: python3

   def prob_decode(probability_array, top=5):
       results = []
       for row in probability_array:
           entries = []
           for i, prob in enumerate(row):
               entries.append({'index': i,
                               'name': str(i),
                               'prob': prob})

           entries = sorted(entries,
                            key=itemgetter('prob'),
                            reverse=True)[:top]

           for entry in entries:
               entry['prob'] = '{:.3f}'.format(entry['prob'])
           results.append(entries)

       return results

``results`` is then a list of dicts in the format ``[{'index': class_index, 'name': class_name, 'prob': class_probability}, ...]``. In the case of the MNIST dataset, the index is the same as the class name (digits 0-9).

.. _examples: https://github.com/merantix/picasso/tree/master/picasso/examples

.. _MNIST: http://yann.lecun.com/exdb/mnist/

.. _VGG16: http://www.robots.ox.ac.uk/~vgg/research/very_deep/

.. _Sequential: https://keras.io/models/sequential/

.. _Keras model code: https://github.com/merantix/picasso/blob/master/picasso/ml_frameworks/keras/model.py

.. _Keras MNIST example: https://github.com/merantix/picasso/blob/master/picasso/examples/keras/util.py

.. _PIL Image: http://pillow.readthedocs.io/en/latest/reference/Image.html

.. [#] We hope to remove these limitations in the future to accomodate a wider variety of possible graph topologies while still maintaining separation between the visualization and model implementation as much as possible.
