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

This endpoint needs at least 2 arguments (``image=X`` and ``visualizer=Y``) in the query string.

.. code-block:: bash

  curl "localhost:5000/api/visualize?image=0&visualizer=PartialOcclusion" -b /path/to/cookie -c /path/to/cookie

output:

.. code-block:: json

  {
    "output": [
      {
        "example_filename": "1496440342.3700328Image.png",
        "input_filename": "Image.png",
        "predict_probs": [
          {
            "index": 2,
            "name": "2",
            "prob": "0.769"
          },
          {
            "index": 8,
            "name": "8",
            "prob": "0.133"
          },
          {
            "index": 3,
            "name": "3",
            "prob": "0.064"
          },
          {
            "index": 7,
            "name": "7",
            "prob": "0.012"
          },
          {
            "index": 5,
            "name": "5",
            "prob": "0.009"
          }
        ],
        "result_filenames": [
          "1496440342.43444780_Image.png",
          "1496440342.6356451_Image.png",
          "1496440342.8196582_Image.png",
          "1496440343.0056613_Image.png",
          "1496440343.1946724_Image.png"
        ]
      }
    ]
  }
