import numpy as np
from PIL import Image

from picasso.ml_frameworks.keras.model import KerasModel


MNIST_DIM = (28, 28)


class KerasMNISTModel(KerasModel):

    def preprocess(self, raw_inputs):
        """Convert images into the format required by our model.

        Our model requires that inputs be grayscale (mode 'L'), be resized to
        `MNIST_DIM`, and be represented as float32 numpy arrays in range
        [0, 1].

        """
        image_arrays = []
        for raw_im in raw_inputs:
            im = raw_im.convert('L')
            im = im.resize(MNIST_DIM, Image.ANTIALIAS)
            arr = np.array(im)
            image_arrays.append(arr)

        inputs = np.array(image_arrays)
        return inputs.reshape(len(inputs),
                              MNIST_DIM[0],
                              MNIST_DIM[1], 1).astype('float32') / 255
