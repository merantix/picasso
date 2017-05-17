===============================
Picasso
===============================


.. image:: https://img.shields.io/pypi/v/picasso-viz.svg
        :target: https://pypi.python.org/pypi/picasso-viz

.. image:: https://img.shields.io/travis/merantix/picasso.svg
        :target: https://travis-ci.org/merantix/picasso

.. image:: https://readthedocs.org/projects/picasso/badge/?version=latest
        :target: https://picasso.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/codecov/c/github/merantix/picasso/master.svg   
        :target: https://codecov.io/github/merantix/picasso?branch=master


A CNN model visualizer

See the `Medium post`_ for an introduction to Picasso.

* Free software: Eclipse Public License
* Documentation: https://picasso.readthedocs.io.

If you use Picasso in your research, `please cite our paper`_:

.. code::

        @misc{picasso2017,
              Author = {Ryan Henderson and Rasmus Rothe},
              Title = {Picasso: A Neural Network Visualizer},
              Year = {2017},
              Eprint = {arXiv:1705.05627},
              Url = {https://arxiv.org/abs/1705.05627}
             }

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

#. Start the Flask server

   .. code::

        export FLASK_APP=picasso
        flask run

   Point your browser to ``127.0.0.1:5000`` and you should see the landing page!  When you're done, ``Ctrl+C`` in the terminal to kill your Flask server.

Building the docs
-----------------

The documentation is much more extensive than this README, and includes instructions on getting the Keras VGG16 and Tensorflow NMIST models working, as well as guides on building your own visualizations and using custom models. This assumes you've cloned the repository. First install the required packages:

.. code::

    pip install -e .[docs]

Then build them:

.. code::

    cd docs/
    make html

Then you can open ``_build/html/index.html`` in your browser of choice.

Notes
---------
#. Models generated on Keras using the Theano backend should in principle be supported.  The only difference is the array ordering of convolutions.  I haven't tried this yet though, so an extra config parameter may be needed.

Credits
---------
* Elias_ and Filippo_ for early code contributions and finding bugs and issues.
* John_, Josh_, Rasmus_, and Stefan_ for their careful code review and feedback.
* The favicon is a modification of this photograph_ of the painting "`Les Demoiselles d'Avignon`_", 1907 by Pablo Picasso. Photograph by Max Braun.
* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _photograph: https://www.flickr.com/photos/maxbraun/4045020694
.. _`Les Demoiselles d'Avignon`: https://en.wikipedia.org/wiki/Les_Demoiselles_d%27Avignon
.. _Elias: https://github.com/Sylvus
.. _Filippo: https://github.com/scopelf
.. _John: https://github.com/JohnMcSpedon
.. _Josh: https://github.com/jwayne
.. _Rasmus: https://github.com/rrothe
.. _Stefan: https://github.com/knub
.. _`Medium post`: https://medium.com/merantix/picasso-a-free-open-source-visualizer-for-cnns-d8ed3a35cfc5
.. _`please cite our paper`: https://arxiv.org/abs/1705.05627
