# Note: this settings file duplicates the default settings in the top-level
# file `settings.py`.  If you want to modify settings here, you must export the
# path to this file:
#
# export PICASSO_SETTINGS=/path/to/picasso/picasso/examples/keras/config.py
#
# otherwise, these settings will not be loaded.
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_CLS_PATH = os.path.join(base_dir, 'model.py')
MODEL_CLS_NAME = 'KerasMNISTModel'
DATA_DIR = os.path.join(base_dir, 'data-volume')
