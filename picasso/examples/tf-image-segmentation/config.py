import os

base_dir = os.path.dirname(os.path.abspath(__file__))

MODEL_CLS_PATH = os.path.join(base_dir, 'model.py')
MODEL_CLS_NAME = 'TensorflowImageSegment'
MODEL_LOAD_ARGS = {
    'data_dir': os.path.join(base_dir, 'data-volume'),
    'tf_input_var': 'ResizeBilinear:0',
    'tf_predict_var': 'fcn_8s/conv2d_transpose_2:0',
}
