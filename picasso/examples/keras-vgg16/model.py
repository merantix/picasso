from keras.applications.imagenet_utils import (decode_predictions,
                                               preprocess_input)
import keras.applications.imagenet_utils
import numpy as np
from PIL import Image

from picasso.ml_frameworks.keras.model import KerasModel


VGG16_DIM = (224, 224, 3)


class KerasVGG16Model(KerasModel):

    def preprocess(self, targets):
        image_arrays = []
        for target in targets:
            im = target.resize(VGG16_DIM[:2], Image.ANTIALIAS)
            im = im.convert('RGB')
            arr = np.array(im).astype('float32')
            image_arrays.append(arr)

        all_targets = np.array(image_arrays)
        return preprocess_input(all_targets)

    def decode_prob(self, probability_array):
        r = decode_predictions(probability_array, top=self.top_probs)
        results = [
            [{'code': entry[0],
              'name': entry[1],
              'prob': '{:.3f}'.format(entry[2])}
             for entry in row]
            for row in r
        ]
        classes = keras.applications.imagenet_utils.CLASS_INDEX
        class_keys = list(classes.keys())
        class_values = list(classes.values())

        for result in results:
            for entry in result:
                entry['index'] = int(
                    class_keys[class_values.index([entry['code'],
                                                   entry['name']])])
        return results
