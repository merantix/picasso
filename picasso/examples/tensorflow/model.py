import numpy as np
from PIL import Image

from picasso.models.tensorflow import TFModel

MNIST_DIM = (28, 28)


class TensorflowMNISTModel(TFModel):

    def preprocess(self, raw_inputs):
        """Convert images into the format required by our model.

        Our model requires that inputs be grayscale (mode 'L'), be resized to
        `MNIST_DIM`, and be represented as float32 numpy arrays in range
        [0, 1].

        Args:
            raw_inputs (list of Images): a list of PIL Image objects

        Returns:
            array (float32): num images * height * width * num channels

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
