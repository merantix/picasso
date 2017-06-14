from PIL import Image
from operator import itemgetter
import numpy as np

from picasso.ml_frameworks.tensorflow.model import TFModel


MNIST_DIM = (28, 28)


class TensorflowMNISTModel(TFModel):

    TF_INPUT_VAR = 'convolution2d_input_1:0'

    TF_PREDICT_VAR = 'Softmax:0'

    @staticmethod
    def preprocess(targets):
        image_arrays = []
        for target in targets:
            im = target.convert('L')
            im = im.resize(MNIST_DIM, Image.ANTIALIAS)
            arr = np.array(im)
            image_arrays.append(arr)

        all_targets = np.array(image_arrays)
        return all_targets.reshape(len(all_targets),
                                   MNIST_DIM[0],
                                   MNIST_DIM[1], 1).astype('float32') / 255

    @staticmethod
    def postprocess(output_arr):
        images = []
        for row in output_arr:
            im_array = row.reshape(MNIST_DIM)
            images.append(im_array)

        return images

    @staticmethod
    def prob_decode(probability_array, top=5):
        results = []
        for row in probability_array:
            entries = []
            for i, prob in enumerate(row):
                entries.append({'index': i,
                                'name': str(i),
                                'prob': prob})

            entries = sorted(entries,
                             key=itemgetter('prob'),
                             reverse=True)[:top]

            for entry in entries:
                entry['prob'] = '{:.3f}'.format(entry['prob'])
            results.append(entries)

        return results
