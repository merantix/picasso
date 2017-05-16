from keras.applications.imagenet_utils import (decode_predictions,
                                               preprocess_input)
import keras.applications.imagenet_utils
from PIL import Image
import numpy as np

VGG16_DIM = (224, 224, 3)


def preprocess(targets):
    image_arrays = []
    for target in targets:
        im = target.resize(VGG16_DIM[:2], Image.ANTIALIAS)
        im = im.convert('RGB')
        arr = np.array(im).astype('float32')
        image_arrays.append(arr)

    all_targets = np.array(image_arrays)
    return preprocess_input(all_targets)


def postprocess(output_arr):
    images = []
    for row in output_arr:
        im_array = row.reshape(VGG16_DIM[:2])
        images.append(im_array)

    return images


def prob_decode(probability_array, top=5):
    r = decode_predictions(probability_array, top=top)
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
            entry.update(
                    {'index':
                     int(
                         class_keys[class_values.index([entry['code'],
                                                        entry['name']])]
                     )}
            )
    return results
