import os
import time

import numpy as np
from PIL import Image

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

from picasso.visualizations.base import BaseVisualization


class PartialOcclusion(BaseVisualization):
    """Partial occlusion visualization

    The partial occlusion class blocks out part of the image and checks
    the classification.  Regions where classification probability drops
    significantly are likely very important to classification.

    The visualization can therefore be used to check if the model is
    classifying on the image feature we expect.

    """
    DESCRIPTION = ('Partially occlude image to determine regions '
                   'important to classification')

    REFERENCE_LINK = 'https://arxiv.org/abs/1311.2901'

    ALLOWED_SETTINGS = {
        'Window': ['0.50', '0.40', '0.30', '0.20', '0.10', '0.05'],
        'Strides': ['2', '5', '10', '20', '30'],
        'Occlusion': ['grey', 'black', 'white']
    }

    def __init__(self, model):
        super(PartialOcclusion, self).__init__(model)
        self.predict_tensor = self.get_predict_tensor()

        self.window = 0.10
        self.num_windows = 20
        self.grid_percent = 0.01
        self.occlusion_method = 'white'
        self.occlusion_value = 255
        self.initial_resize = (244, 244)

    def make_visualization(self, inputs, output_dir, settings=None):
        if settings:
            self.update_settings(settings)
            if self.occlusion_method == 'black':
                self.occlusion_value = 0
            elif self.occlusion_method == 'grey':
                self.occlusion_value = 128

        # get class predictions as in ClassProbabilities
        pre_processed_arrays = self.model.preprocess([example['data']
                                                      for example in inputs])
        class_predictions = self.model.sess.run(
            self.model.tf_predict_var,
            feed_dict={self.model.tf_input_var: pre_processed_arrays})
        decoded_predictions = self.model.decode_prob(class_predictions)

        results = []
        for i, example in enumerate(inputs):
            im = example['data']
            im_format = im.format
            if self.initial_resize:
                im = im.resize(self.initial_resize, Image.ANTIALIAS)

            occ_im = self.occluded_images(im)
            predictions = self.model.sess.run(
                self.predict_tensor,
                feed_dict={self.model.tf_input_var:
                           self.model.preprocess(occ_im['occluded_images'])})

            example_im = self.make_example_image(im,
                                                 occ_im['centers_horizontal'],
                                                 occ_im['centers_vertical'],
                                                 occ_im['win_width'],
                                                 occ_im['win_length'],
                                                 occ_im['pad_vertical'],
                                                 occ_im['pad_horizontal'])
            example_filename = '{ts}{fn}'.format(ts=str(time.time()),
                                                 fn=example['filename'])
            example_im.save(
                os.path.join(output_dir, example_filename),
                format=im_format)

            filenames = self.make_heatmaps(
                predictions, output_dir, example['filename'],
                decoded_predictions=decoded_predictions[i])
            results.append({'input_filename': example['filename'],
                            'result_filenames': filenames,
                            'predict_probs': decoded_predictions[i],
                            'example_filename': example_filename})
        return results

    def get_predict_tensor(self):
        # Assume that predict is the softmax
        # tensor in the computation graph
        return self.model.sess.graph.get_tensor_by_name(
            self.model.tf_predict_var.name)

    def update_settings(self, settings):
        def error_string(setting, setting_val):
            return ('{val} is not an acceptable value for '
                    'parameter {param} for visualization'
                    '{vis}.').format(val=setting_val,
                                     param=setting,
                                     vis=self.__class__.__name__)

        if 'Window' in settings:
            if settings['Window'] in self.ALLOWED_SETTINGS['Window']:
                self.window = float(settings['Window'])
            else:
                raise ValueError(error_string(settings['Window'], 'Window'))

        if 'Strides' in settings:
            if settings['Strides'] in self.ALLOWED_SETTINGS['Strides']:
                self.num_windows = int(settings['Strides'])
            else:
                raise ValueError(error_string(settings['Strides'], 'Strides'))

        if 'Occlusion' in settings:
            if settings['Occlusion'] in self.ALLOWED_SETTINGS['Occlusion']:
                self.occlusion_method = settings['Occlusion']
            else:
                raise ValueError(error_string(settings['Occlusion'],
                                              'Occlusion'))

    def make_heatmaps(self, predictions,
                      output_dir, filename,
                      decoded_predictions=None):
        if decoded_predictions:
            relevant_class_indices = [pred['index']
                                      for pred in decoded_predictions]
            predictions = predictions[:, relevant_class_indices]
        stacked_heatmaps = predictions.reshape(self.num_windows,
                                               self.num_windows,
                                               predictions.shape[-1])
        filenames = []
        for i in range(predictions.shape[-1]):
            grid = stacked_heatmaps[:, :, i]
            pyplot.axis('off')
            if i == 0:
                im = pyplot.imshow(grid, vmin=0, vmax=1)
                pyplot.axis('off')
                im.axes.get_xaxis().set_visible(False)
                im.axes.get_yaxis().set_visible(False)
            else:
                im.set_data(grid)
            hm_filename = '{ts}{label}_{fn}'.format(ts=str(time.time()),
                                                    label=str(i),
                                                    fn=filename)
            pyplot.savefig(os.path.join(output_dir, hm_filename),
                           format='PNG', bbox_inches='tight', pad_inches=0)
            filenames.append(hm_filename)
        return filenames

    def occluded_images(self, im):
        width = im.size[0]
        length = im.size[1]
        win_width = round(self.window * width)
        win_length = round(self.window * length)
        pad_horizontal = win_width // 2
        pad_vertical = win_length // 2
        centers_horizontal, centers_vertical = self.get_centers(
            width, length, win_width, win_length, pad_horizontal, pad_vertical,
            self.num_windows)
        upper_left_corners = np.array(
            [(w - pad_vertical, v - pad_horizontal)
             for w in centers_vertical
             for v in centers_horizontal]
        )

        images = []
        for corner in upper_left_corners:
            arr = np.array(im)
            self.add_occlusion_to_arr(arr, corner,
                                      win_width, win_length,
                                      occ_val=self.occlusion_value)
            images.append(
                Image.fromarray(arr)
            )

        return {'occluded_images': images,
                'centers_horizontal': centers_horizontal,
                'centers_vertical': centers_vertical,
                'win_width': win_width,
                'win_length': win_length,
                'pad_horizontal': pad_horizontal,
                'pad_vertical': pad_vertical}

    def make_example_image(self, im,
                           centers_horizontal, centers_vertical,
                           win_width, win_length, pad_vertical,
                           pad_horizontal, output_size=(244, 244)):
        arr = np.array(im)
        # add an example occlusion
        self.add_occlusion_to_arr(arr,
                                  (centers_vertical[1] - pad_vertical,
                                   centers_horizontal[1] - pad_horizontal),
                                  win_width, win_length, occ_val=100)
        # add grid
        g_pad_vertical = round(self.grid_percent * im.size[1]) or 1
        g_pad_horizontal = round(self.grid_percent * im.size[0]) or 1
        w_grid = 2 * g_pad_horizontal
        l_grid = 2 * g_pad_vertical
        upper_left_corners = np.array(
            [(w - g_pad_vertical, v - g_pad_horizontal)
             for w in centers_vertical
             for v in centers_horizontal]
        )
        for corner in upper_left_corners:
            self.add_occlusion_to_arr(arr, corner,
                                      w_grid, l_grid)
        return Image.fromarray(arr)

    @staticmethod
    def get_centers(width, length,
                    win_width, win_length,
                    pad_horizontal, pad_vertical,
                    num_windows):
        centers_horizontal = np.linspace(pad_horizontal,
                                         width - pad_horizontal,
                                         num_windows).astype('int')
        centers_vertical = np.linspace(pad_vertical,
                                       length - pad_vertical,
                                       num_windows).astype('int')
        return centers_horizontal, centers_vertical

    @staticmethod
    def add_occlusion_to_arr(arr, upper_left_corner,
                             width_horizontal,
                             width_vertical,
                             occ_val=0):
        arr[upper_left_corner[0]:
            upper_left_corner[0] + width_vertical,
            upper_left_corner[1]:
            upper_left_corner[1] + width_horizontal] = occ_val
