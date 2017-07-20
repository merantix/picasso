from picasso.visualizations.base import BaseVisualization
import os
import matplotlib as mpl
mpl.matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time
import numpy as np
import scipy.misc
import random

class SegmentProbabilities(BaseVisualization):
    DESCRIPTION = 'Visualize segmented Picture'

    def __init__(self, model):
        super(SegmentProbabilities, self).__init__(model)

        self.background_class_index = 0

        # TODO Random Generator for colors
        self.colors = [[0, 255, 0, 122], [255, 0, 0, 122], [0, 0, 255, 122],
                       [0, 255, 255, 122], [255, 0, 127, 122], [255, 255, 102, 122]]

    def make_visualization(self, inputs,
                           output_dir, settings=None):

        def fast_overlay(input_image, segmentation, color):
            color = np.array(color).reshape(1, 4)
            shape = input_image.shape
            segmentation = segmentation.reshape(shape[0], shape[1], 1)

            output = np.dot(segmentation, color)
            output = scipy.misc.toimage(output, mode="RGBA")

            background = scipy.misc.toimage(input_image)
            background.paste(output, box=None, mask=output)

            return np.array(background)

        def removekey(d, key):
            r = dict(d)
            del r[key]
            return r

        pre_processed_arrays = self.model.preprocess([example['data']
                                                     for example in inputs])

        predictions = list()
        for array in pre_processed_arrays:
            predictions.append(self.model.sess.run(self.model.tf_predict_var,
                                                   feed_dict={self.model.tf_input_var: np.expand_dims(array, 0)}))

        decoded_probabilities, class_dict, _ = self.model.decode_prob(predictions)

        filtered_predictions = np.argmax(decoded_probabilities, axis=3)
        class_dict_m = removekey(class_dict, self.background_class_index)

        results = []
        for i, inp in enumerate(inputs):
            relevant_classes = np.unique(filtered_predictions[i]).astype(int)
            relevant_classes = list(filter(lambda x: x != self.background_class_index, relevant_classes))

            prediction_filename = '%04x.png' % random.getrandbits(4 * 4)

            cmaps_colors = np.array(self.colors)/255
            cmaps_colors[:, -1:] = 1
            cmap = mpl.colors.ListedColormap(cmaps_colors)
            colors_dict = {key: self.colors[ii] for ii, key in enumerate(class_dict_m.keys())}

            class_list = list(class_dict_m.values())
            steps = int(255 / (len(class_list)))
            yticks = [i + steps / 2 for i in range(0, 255, steps)]

            fig, ax = plt.subplots(figsize=(10, (10 * pre_processed_arrays[i].shape[1]) / pre_processed_arrays[i].shape[0]))
            out_image = pre_processed_arrays[i]

            for rcl in relevant_classes:
                out_image = fast_overlay(out_image, (filtered_predictions[i] == rcl).astype("uint8"),
                                         color=colors_dict[rcl])

            im = ax.imshow(out_image, cmap=cmap)
            im.axes.get_xaxis().set_visible(False)
            im.axes.get_yaxis().set_visible(False)

            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="3%")
            cbar = plt.colorbar(im,  cax=cax, ticks=yticks)
            cbar.ax.set_yticklabels(class_list)

            plt.savefig(os.path.join(output_dir, prediction_filename), bbox_inches='tight', dpi=100)

            results.append({'input_filename': inp['filename'],
                            'output_filename': prediction_filename,
                            'width_multiple': (244 * pre_processed_arrays[i].shape[1]) / pre_processed_arrays[i].shape[0]})

        return results
