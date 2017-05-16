# Note: this settings file duplicates the default settings in the top-level
# file `settings.py`.  If you want to modify settings here, you must export the
# path to this file:
#
# export PICASSO_SETTINGS=/path/to/picasso/picasso/examples/keras/config.py
#
# otherwise, these settings will not be loaded.
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

BACKEND_ML = 'keras'
BACKEND_PREPROCESSOR_NAME = 'preprocess'
BACKEND_PREPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
BACKEND_POSTPROCESSOR_NAME = 'postprocess'
BACKEND_POSTPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
BACKEND_PROB_DECODER_NAME = 'prob_decode'
BACKEND_PROB_DECODER_PATH = os.path.join(base_dir, 'util.py')
DATA_DIR = os.path.join(base_dir, 'data-volume')
