from PIL import Image
import numpy as np
import pytest

from picasso import app as _app


@pytest.fixture
def app():
    return _app


@pytest.fixture(scope='session')
def random_image_files(tmpdir_factory):
    fn = tmpdir_factory.mktemp('images')
    for i in range(4):
        imarray = np.random.rand(10**i, 10**i, 3) * 255
        img = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
        img.save(str(fn.join('{}.png'.format(i))), 'PNG')
    return fn


@pytest.fixture
def example_prob_array():
    return np.random.random((3, 10))


@pytest.fixture
def base_model():
    from picasso.ml_frameworks.model import BaseModel

    class BaseModelForTest(BaseModel):
        def load(self, data_dir):
            pass
    return BaseModelForTest()


@pytest.fixture
def tensorflow_model():
    from picasso.ml_frameworks.tensorflow.model import TFModel

    tfm = TFModel(TF_PREDICT_VAR='Softmax:0',
                  TF_INPUT_VAR='convolution2d_input_1:0')

    return tfm
