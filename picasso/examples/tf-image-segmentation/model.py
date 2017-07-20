import numpy as np
from picasso.models.tensorflow import TFModel
from PIL import Image


class TensorflowImageSegment(TFModel):
    def __init__(self):
        self.class_dict = {0: 'background',
                           1: 'aeroplane',
                           2: 'bicycle',
                           3: 'bird',
                           4: 'boat',
                           5: 'bottle',
                           6: 'bus',
                           7: 'car',
                           8: 'cat',
                           9: 'chair',
                           10: 'cow',
                           11: 'diningtable',
                           12: 'dog',
                           13: 'horse',
                           14: 'motorbike',
                           15: 'person',
                           16: 'potted-plant',
                           17: 'sheep',
                           18: 'sofa',
                           19: 'train',
                           20: 'tv/monitor',
                           }

        self.custom_class_dict = {0: 'background',
                                  1: 'bicycle',
                                  2: 'bus',
                                  3: 'car',
                                  4: 'horse',
                                  5: 'motorbike',
                                  6: 'person',
                                  }
        self.class_trans_custom = self.transform_class_dict()
        self.custom_trans_class = {v: k for k, v in self.class_trans_custom.items()}

    def transform_class_dict(self):
        class_trans_lookup = dict()
        for j in self.class_dict.keys():
            for i in self.custom_class_dict.keys():
                if self.class_dict[j] == self.custom_class_dict[i]:
                    class_trans_lookup[j] = i

        return class_trans_lookup

    def preprocess(self, targets):
        image_arrays = []
        for target in targets:
            shapes = tuple((np.round(np.array(target.size) / 32) * 32).astype(int))
            im = target.resize(shapes)
            arr = np.array(im)
            image_arrays.append(arr)
        return np.array(image_arrays)

    def postprocess(self, output_arr):
        images = []
        for row in output_arr:
            im_array = np.array(row)
            images.append(im_array)
        return images

    def decode_prob(self, probability_array):
        def softmax(x):
            if x.ndim == 1:
                x = x.reshape((1, -1))
            max_x = np.max(x, axis=1).reshape((-1, 1))
            exp_x = np.exp(x - max_x)
            return exp_x / np.sum(exp_x, axis=1).reshape((-1, 1))

        output_values = []
        for row in probability_array:
            values = np.zeros([row.shape[1], row.shape[2], len(self.custom_class_dict.keys())])
            for i in range(row[0].shape[0]):
                for j in range(row[0].shape[1]):
                    softmax_output = softmax(row[0][i, j, :])
                    values[i, j, :] = softmax_output[0][list(self.class_trans_custom.keys())]

            output_values.append(values)

        return np.array(output_values), self.custom_class_dict, self.custom_trans_class
