import os
import time

import numpy as np
import tensorflow as tf

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.misc
from PIL import Image
import random

from picasso.visualizations.base import BaseVisualization


class SaliencySegMaps(BaseVisualization):
    """Derivative of classification with respect to input pixels

    Saliency maps are a way of showing which inputs matter most to
    classification.  The derivative of a class probability with
    respect to each input pixel are found with backpropagation.
    High values for the derivative indicate pixels important to
    classification (as changing them would change the classification).

    """
    DESCRIPTION = 'Saliency Maps for Segmentation'

    def __init__(self, model):
        super(SaliencySegMaps, self).__init__(model)

        self.logit_tensor = self.model.tf_predict_var

        self.input_shape = self.model.tf_input_var.get_shape()[1:].as_list()

        self.background_class_index = 0

        self.n_rand = 5

    def get_gradient_wrt_class_and_pixel(self, class_index, pixel_index):
        class_logit = tf.slice(self.logit_tensor,
                               [0, pixel_index[0], pixel_index[1], class_index],
                               [1, 1, 1, 1])
        return tf.gradients(class_logit, self.model.tf_input_var)

    def make_visualization(self, inputs, output_dir, settings=None):

        np.random.seed(0)

        # See Github TensorVision/tensorvision/utils.py
        def fast_overlay(input_image, segmentation, color=[0, 255, 0, 122]):
            color = np.array(color).reshape(1, 4)
            shape = input_image.shape
            segmentation = segmentation.reshape(shape[0], shape[1], 1)

            output = np.dot(segmentation, color)
            output = scipy.misc.toimage(output, mode="RGBA")

            background = scipy.misc.toimage(input_image)
            background.paste(output, box=None, mask=output)

            return np.array(background)

        def set_alpha(input_image, alpha=185):
            pil_image = Image.fromarray(input_image)
            pil_image.putalpha(alpha)
            return np.array(pil_image)

        def nonzero_indices(z):
            shapes = np.nonzero(z)
            height, width = shapes[0], shapes[1]
            return height, width

        def largest_indices(ary, n):
            flat = ary.flatten()
            indices = np.argpartition(flat, -n)[-n:]
            indices = indices[np.argsort(-flat[indices])]
            return np.unravel_index(indices, ary.shape)

        pre_processed_arrays = self.model.preprocess([example['data']
                                                     for example in inputs])

        predictions = list()
        for array in pre_processed_arrays:
            predictions.append(self.model.sess.run(self.model.tf_predict_var,
                                                   feed_dict={self.model.tf_input_var: np.expand_dims(array, 0)}))

        decoded_probabilities, class_dict, custom_trans_class = self.model.decode_prob(predictions)

        filtered_predictions = np.argmax(decoded_probabilities, axis=3)

        results = []
        for i, inp in enumerate(inputs):

            output_fns = []
            titles = []

            relevant_classes = np.unique(filtered_predictions[i]).astype(int)
            relevant_classes = list(filter(lambda x: x != self.background_class_index or
                                                     np.sum(filtered_predictions[i] == x) < 100, relevant_classes))

            for cl in relevant_classes:
                class_indices = (filtered_predictions[i] == cl).astype(int)
                height, width = nonzero_indices(class_indices)

                indices = np.array([[h, w] for h, w in zip(height, width)])
                rand_indices = indices[np.random.randint(len(indices), size=self.n_rand)]

                saliency_maps = []
                for index in rand_indices:
                    gradient = self.get_gradient_wrt_class_and_pixel(custom_trans_class[cl], index)
                    saliency_maps.append(self.model.sess.run(gradient, feed_dict={self.model.tf_input_var:
                                                                np.expand_dims(pre_processed_arrays[i], 0)})[0][0])

                output_arrays = np.array(saliency_maps)
                # take the maximum channel
                output_arrays = np.abs(output_arrays.max(-1))
                saliency_map = np.sum(np.array(output_arrays), 0)

                output_fn = '%04x.png' % random.getrandbits(4 * 4)

                alpha_image = set_alpha(pre_processed_arrays[i])
                alpha_image = fast_overlay(alpha_image, class_indices)

                plt.figure(figsize=(np.array(pre_processed_arrays[i].shape[:2])/30))
                im = plt.imshow(alpha_image)

                y_x = largest_indices(saliency_map, 1000)
                y, x = y_x[0], y_x[1]

                plt.scatter(x, y, s=0.1, c=saliency_map[y, x], cmap="Reds",
                            vmin=np.min(saliency_map[y, x]), vmax=sorted(saliency_map[y, x])[-201:-200])

                for index in rand_indices:
                    plt.scatter(index[1], index[0], s=1, color="c")

                plt.axis('off')
                im.axes.get_xaxis().set_visible(False)
                im.axes.get_yaxis().set_visible(False)

                plt.savefig(os.path.join(output_dir, output_fn), bbox_inches='tight', pad_inches=0)
                output_fns.append(output_fn)

                # TODO CHANGE THE TUPLE
                value = np.mean([decoded_probabilities[i][tuple(rand_indices[k])][cl] for k in range(self.n_rand)])
                titles.append({"name": class_dict[cl], "prob": str(np.round(value*100, decimals=2))+"%"})

            results.append({'input_file_name': inp['filename'],
                            'predict_probs': titles,
                            'gradient_image_names': output_fns,
                            'width_multiple': (244 * pre_processed_arrays[i].shape[1]) / pre_processed_arrays[i].shape[0]})

        return results
