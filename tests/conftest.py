###############################################################################
# Copyright (c) 2017 Merantix GmbH
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Ryan Henderson - initial API and implementation and/or initial
#    documentation
###############################################################################
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
    from picasso.models.base import BaseModel
    class BaseModelForTest(BaseModel):
        def load(self, data_dir):
            pass
    return BaseModelForTest()


@pytest.fixture
def tensorflow_model():
    from picasso.models.tensorflow import TFModel
    return TFModel()
