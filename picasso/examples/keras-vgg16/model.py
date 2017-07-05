from keras.applications import imagenet_utils
import numpy as np
from PIL import Image

from picasso.models.keras import KerasModel

VGG16_DIM = (224, 224, 3)


class KerasVGG16Model(KerasModel):

    def preprocess(self, raw_inputs):
        """
        Args:
            raw_inputs (list of Images): a list of PIL Image objects
        Returns:
            array (float32): num images * height * width * num channels
        """
        image_arrays = []
        for raw_im in raw_inputs:
            im = raw_im.resize(VGG16_DIM[:2], Image.ANTIALIAS)
            im = im.convert('RGB')
            arr = np.array(im).astype('float32')
            image_arrays.append(arr)

        all_raw_inputs = np.array(image_arrays)
        return imagenet_utils.preprocess_input(all_raw_inputs)

    def decode_prob(self, class_probabilities):
        r = imagenet_utils.decode_predictions(class_probabilities,
                                              top=self.top_probs)
        results = [
            [{'code': entry[0],
              'name': entry[1],
              'prob': '{:.3f}'.format(entry[2])}
             for entry in row]
            for row in r
        ]
        classes = imagenet_utils.CLASS_INDEX
        class_keys = list(classes.keys())
        class_values = list(classes.values())

        for result in results:
            for entry in result:
                entry['index'] = int(
                    class_keys[class_values.index([entry['code'],
                                                   entry['name']])])
        return results
