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

    #: :obj:`str`: which backend to use
    BACKEND_ML = 'keras'

    #: :obj:`str`: name of the preprocess function
    BACKEND_PREPROCESSOR_NAME = 'preprocess'

    #: :obj:`str`: filepath of the preprocess function
    BACKEND_PREPROCESSOR_PATH = os.path.join(
        base_dir, 'examples', 'keras', 'util.py')

    #: :obj:`str`: name of the postprocess function
    BACKEND_POSTPROCESSOR_NAME = 'postprocess'

    #: :obj:`str`: filepath of the postprocess function
    BACKEND_POSTPROCESSOR_PATH = os.path.join(
        base_dir, 'examples', 'keras', 'util.py')

    #: :obj:`str`: name of the probability decoder function
    BACKEND_PROB_DECODER_NAME = 'prob_decode'

    #: :obj:`str`: filepath of the probability decoder function
    BACKEND_PROB_DECODER_PATH = os.path.join(
        base_dir, 'examples', 'keras', 'util.py')

    #: :obj:`str`: path to directory containing weights and graph
    DATA_DIR = os.path.join(
        base_dir, 'examples', 'keras', 'data-volume')
