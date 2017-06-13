import os

base_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_CLS_PATH = os.path.join(base_dir, 'model.py')
MODEL_CLS_NAME = 'TensorflowMNISTModel'
BACKEND_TF_PREDICT_VAR = 'Softmax:0'
BACKEND_TF_INPUT_VAR = 'convolution2d_input_1:0'
DATA_DIR = os.path.join(base_dir, 'data-volume')
