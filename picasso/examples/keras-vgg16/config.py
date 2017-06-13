import os

base_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_CLS_PATH = os.path.join(base_dir, 'model.py')
MODEL_CLS_NAME = 'KerasVGG16Model'
DATA_DIR = os.path.join(base_dir, 'data-volume')
