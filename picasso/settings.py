import os

base_dir = os.path.dirname(__file__)  # only for default config


class Default:
    """Default settings for the Flask app.

    The Flask app uses these settings if no custom settings are defined.  You
    can define custom settings by creating a Python module, defining global
    variables in that module, and setting the environment variable
    `PICASSO_SETTINGS` to the path to that module.

    If `PICASSO_SETTINGS` is not set, or if any particular setting is not
    defined in the indicated module, then the Flask app uses these default
    settings.

    """
    # :obj:`str`: filepath of the module containing the model to run
    MODEL_CLS_PATH = os.path.join(
        base_dir, 'examples', 'keras', 'model.py')

    # :obj:`str`: name of model class
    MODEL_CLS_NAME = 'KerasMNISTModel'

    # :obj:`dict`: dictionary of args to pass to the `load` method of the
    # model instance.
    MODEL_LOAD_ARGS = {
        'data_dir': os.path.join(base_dir, 'examples', 'keras', 'data-volume'),
    }
