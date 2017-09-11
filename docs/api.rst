========
API
========
Since v0.2.0, Picasso allows you to call parts of its functionality via an API. The API is intended to be RESTful and provides responses as JSON. The following chapter gives you some insight on how to use the API.

Currently the session is stored in a cookie to allow reuse of uploaded images and separate the user space on the server.

All files referenced in the API can be directly accessed via ``/inputs/<filename>`` and ``/outputs/<filename>``.


GET /api/
#########

Right now this is only a placeholder. It could potentially be used to start a session to authenticate a user and to display the API version.

.. code-block:: bash

  curl "localhost:5000/api/"

Output:

.. code-block:: json

  {
    "message": "Picasso v0.2.0. Developer documentation coming soon!",
    "version": "v0.2.0"
  }




POST /api/images
################

Upload an image. It returns the filename and a UID in JSON

.. code-block:: bash

  curl -F "file=@/path/to/image.png" localhost:5000/api/images -b /path/to/cookie -c /path/to/cookie

Output:

.. code-block:: json

  {
    "file": "image.png",
    "ok": "true",
    "uid": 0
  }




GET /api/images
###############
List all images uploaded via this API

.. code-block:: bash

  curl "localhost:5000/api/images" -b /path/to/cookie -c /path/to/cookie

Output:

.. code-block:: json

  {
    "images": [
      {
        "filename": "Screen_Shot_2016-11-08_at_22.57.51.png",
        "uid": 0
      },
      {
        "filename": "Image.png",
        "uid": 1
      }
    ]
  }




GET /api/visualizers
###############
List all available visualizers

.. code-block:: bash

  curl "localhost:5000/api/visualizers" -b /path/to/cookie -c /path/to/cookie

Output:

.. code-block:: json

  {
    "visualizers": [
      {
        "name": "ClassProbabilities"
      },
      {
        "name": "PartialOcclusion"
      },
      {
        "name": "SaliencyMaps"
      }
    ]
  }




GET /api/visualizers/<vis_name>
###############
List all available settings for visualizer ``<viz_name>``

.. code-block:: bash

  curl "localhost:5000/api/visualizers/PartialOcclusion" -b /path/to/cookie -c /path/to/cookie

Output:

.. code-block:: json

  {
    "settings": {
      "Occlusion": [
        "grey",
        "black",
        "white"
      ],
      "Strides": [
        "2",
        "5",
        "10",
        "20",
        "30"
      ],
      "Window": [
        "0.50",
        "0.40",
        "0.30",
        "0.20",
        "0.10",
        "0.05"
      ]
    }
  }

returns an empty settings object when no settings available:

.. code-block:: json

  {
    "settings": {}
  }




GET /api/visualize
###################

This endpoint needs at least 2 arguments (``image=X`` and ``visualizer=Y``) in the query string. Each response is guaranteed to have at least the following attributes:

=======================   ===================== =========
``input_file_name``       String
``predict_probs``         List of probabilities
``has_output``            boolean               if this is ``True`` the output will also have a list ``output_file_names``
``has_processed_input``   boolean               if this is ``True`` the output will also have an attribute ``processed_input_file_name``
=======================   ===================== =========

.. code-block:: bash

  curl "localhost:5000/api/visualize?image=0&visualizer=PartialOcclusion" -b /path/to/cookie -c /path/to/cookie

output:

.. code-block:: json

  {
    "has_output": true,
    "has_processed_input": true,
    "input_file_name": "test.png",
    "output_file_names": [
      "1504440185.6014730_test.png",
      "1504440185.6964661_test.png",
      "1504440185.7823882_test.png",
      "1504440185.86981823_test.png",
      "1504440185.9575094_test.png"
    ],
    "predict_probs": [
      {
        "index": 8,
        "name": "8",
        "prob": "0.171"
      },
      {
        "index": 6,
        "name": "6",
        "prob": "0.125"
      },
      {
        "index": 2,
        "name": "2",
        "prob": "0.122"
      },
      {
        "index": 5,
        "name": "5",
        "prob": "0.119"
      },
      {
        "index": 0,
        "name": "0",
        "prob": "0.098"
      }
    ],
    "processed_input_file_name": "1504440185.5588531test.png"
  }


