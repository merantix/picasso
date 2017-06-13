import os

base_dir = os.path.dirname(__file__)  # only for default config


class Default:
    """Default configuration settings

    The app will use these settings if none are specified. That is,
    if no configuration file is specified by PICASSO_SETTINGS
    or any individual setting is specified by environment variable.
    These are, in effect, "settings of last resort."

    The paths will automatically be generated based on the location of
    the source.
    """

    #: :obj:`str`: filepath of the module containing the model to run
    MODEL_CLS_PATH = os.path.join(base_dir, 'examples', 'keras', 'model.py')

    #: :obj:`str`: name of model class
    MODEL_CLS_NAME = 'KerasMNISTModel'

    #: :obj:`str`: path to directory containing weights and graph
    DATA_DIR = os.path.join(
        base_dir, 'examples', 'keras', 'data-volume')
