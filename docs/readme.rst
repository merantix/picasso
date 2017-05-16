===============================
Picasso
===============================

A CNN model visualizer


* Free software: Eclipse Public License 
* Documentation: https://picasso.readthedocs.io.


Quickstart
----------

Picasso uses **Python 3.5+** so use a virtual environment if necessary (e.g. ``virtualenv env --python=python3``) and **activate it!**

#. Install with pip or from source.

   With pip:

   .. code::

        pip install picasso-viz

   From the repository:

   .. code::

        git clone git@github.com:merantix/picasso.git
        cd picasso
        pip install -e .
        
   Note: you'll need the Tensorflow backend for Keras for these examples to work.  Make sure your ``~/.keras/keras.json`` file looks like:
   
   .. code::
        
        {
            "backend": "tensorflow",
            "image_dim_ordering": "tf",
            "floatx": "float32",
            "epsilon": 1e-07
        }

#. Optional (untested!): install Tensorflow with GPU support
    
   .. code::
    
        pip uninstall tensorflow
        pip install --upgrade tensorflow-gpu
        
#. Start the Flask server

   .. code::

        export FLASK_APP=picasso
        flask run

   Point your browser to ``127.0.0.1:5000`` and you should see the landing page!  When you're done, ``Ctrl+C`` in the terminal to kill your Flask server.
   
#. By default, the visualizer starts a Keras MNIST example.  We've also included a Keras VGG16 example. To use, it you'll need to get the VGG16 graph and weights.  We've included a small script to do this.

   #. Setup VGG16:
   
      .. code::
      
          python picasso/examples/keras-vgg16/prepare_model.py
          
      NOTE: if you installed with ``pip``, you'll need to find the location of this file in the site packages.  ``pip show picasso_viz`` will tell you the location. For instance, if ``pip show picasso_viz`` shows you ``/home/ryan/test/env/lib/python3.5/site-packages``, then the above command should be:

      .. code::

          python /home/ryan/test/env/lib/python3.5/site-packages/picasso/examples/keras-vgg16/prepare_model.py
      
      If this script fails, you might be behind a proxy.  You can download the necessary files manually.
          
      .. code::

           mkdir ~/.keras/models # If directory doesn't exist
           wget --no-check-certificate -P ~/.keras/models/ https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg16_weights_tf_dim_ordering_tf_kernels.h5
           wget --no-check-certificate -P ~/.keras/models/ https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json 
           
      Run the script again, and you should be good to go!

   #. Point to the correct configuration (making sure to use the correct path to your directory): 
   
      .. code::
      
          export PICASSO_SETTINGS=/absolute/path/to/repo/picasso/picasso/examples/keras-vgg16/config.py

      Again, if you installed with ``pip install picasso-viz``, this will look something like:

      .. code::

          export PICASSO_SETTINGS=/home/ryan/test/env/lib/python3.5/site-packages/picasso/examples/keras-vgg16/config.py

      You can check the ``pip show picasso_viz`` command for the base directory.

   #. Start Flask ``flask run``.  If it worked, the "Current checkpoint" label should have changed on the landing page.

Building the docs
-----------------
Assuming you've cloned the repository, install the required packages:

      .. code::
      
          pip install -e .[docs] 
          
Then build them:

      .. code::
          
          cd docs/
          make html

Then you can open ``_build/html/index.html`` in your browser of choice.

Running the tests
-----------------
Install the test requirements:

      .. code::
      
          pip install -e .[test] 

Then run with:

      .. code::
      
          py.test 

Notes
-----
#. This should be considered alpha software.  You will encounter bugs and issues. Don't deploy this to a live server, probably...
#. Models generated on Keras using the Theano backend should in principle be supported.  The only difference is the array ordering of convolutions.  I haven't tried this yet though, so an extra config parameter may be needed.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
