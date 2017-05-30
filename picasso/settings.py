import os

base_dir = os.path.dirname(__file__)  # only for default config


class Default:
    """Default configuration settings.

    These settings are overridden by any settings defined in the Python module
    referred to by the environment variable `PICASSO_SETTINGS`.  If
    `PICASSO_SETTINGS` is not set, or if any particular parameter value is
    not set in the indicated module, then the app uses these settings.

    """
    # :obj:`str`: filepath of the module containing the model to run
    MODEL_CLS_PATH = os.path.join(
        base_dir, 'examples', 'keras', 'model.py')

    # :obj:`str`: name of model class
    MODEL_CLS_NAME = 'KerasMNISTModel'

    # :obj:`str`: path to directory containing weights and graph
    DATA_DIR = os.path.join(
        base_dir, 'examples', 'keras', 'data-volume')

