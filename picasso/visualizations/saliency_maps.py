###############################################################################
# Copyright (c) 2017 Merantix GmbH
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Ryan Henderson - initial API and implementation and/or initial
#    documentation
#    Josh Chen - refactor and class config
###############################################################################
import os
import time

import numpy as np
import tensorflow as tf

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

from picasso.visualizations.base import BaseVisualization


class SaliencyMaps(BaseVisualization):
    """Derivative of classification with respect to input pixels

    Saliency maps are a way of showing which inputs matter most to
    classification.  The derivative of a class probability with
    respect to each input pixel are found with backpropagation.
    High values for the derivative indicate pixels important to
    classification (as changing them would change the classification).

    """
    DESCRIPTION = ('See maximal derivates against class with respect '
                   'to input')

    REFERENCE_LINK = 'https://arxiv.org/pdf/1312.6034'

    ALLOWED_SETTINGS = {'Transparency': ['0.0', '0.25', '0.5', '0.75']}

    @property
    def transparency(self):
        return float(self._transparency)

    def __init__(self, model, logit_tensor_name=None):
        super().__init__(model)
        if logit_tensor_name:
            self.logit_tensor = self.model.sess.graph.get_tensor_by_name(
                logit_tensor_name)
        else:
            self.logit_tensor = self.get_logit_tensor()

        self.input_shape = self.model.tf_input_var.get_shape()[1:].as_list()

    def get_gradient_wrt_class(self, class_index):
        gradient_name = 'bv_{class_index}_gradient'.format(
            class_index=class_index)
        try:
            return self.model.sess.graph.get_tensor_by_name(
                '{}:0'.format(gradient_name))
        except KeyError:
            class_logit = tf.slice(self.logit_tensor,
                                   [0, class_index],
                                   [1, 1])
            return tf.gradients(class_logit,
                                self.model.tf_input_var,
                                name=gradient_name)[0]

    def make_visualization(self, inputs, output_dir):

        pre_processed_arrays = self.model.preprocess([example['data']
                                                     for example in inputs])

        # get predictions
        predictions = self.model.sess.run(self.model.tf_predict_var,
                                          feed_dict={self.model.tf_input_var:
                                                     pre_processed_arrays})
        decoded_predictions = self.model.decode_prob(predictions)

        results = []
        for i, inp in enumerate(inputs):
            class_gradients = []
            relevant_class_indices = [pred['index']
                                      for pred in decoded_predictions[i]]
            gradients_wrt_class = [self.get_gradient_wrt_class(index)
                                   for index in relevant_class_indices]
            for gradient_wrt_class in gradients_wrt_class:
                class_gradients.append([self.model.sess.run(
                    gradient_wrt_class,
                    feed_dict={self.model.tf_input_var: [arr]})
                    for arr in pre_processed_arrays])

            output_arrays = np.array([gradient[i]
                                      for gradient in class_gradients])
            # if images are color, take the maximum channel
            if output_arrays.shape[-1] == 3:
                output_arrays = output_arrays.max(-1)
            # we care about the size of the derivative, not the sign
            output_arrays = np.abs(output_arrays)

            # We want each array to be represented as a 1-channel image of
            # the same size as the model's input image.
            output_images = output_arrays.reshape([-1] + self.input_shape[0:2])

            output_fns = []
            pyplot.clf()
            for j, output_image in enumerate(output_images):
                output_fn = '{fn}-{j}-{ts}.png'.format(ts=str(time.time()),
                                                       j=j,
                                                       fn=inp['filename'])

                if j == 0:
                    pyplot.imshow(inputs[i]['data']
                                  .resize(output_image.shape)
                                  .convert('RGB'),
                                  alpha=self.transparency)

                    im = pyplot.imshow(output_image,
                                       alpha=1. - self.transparency,
                                       cmap='inferno')
                    pyplot.axis('off')
                    im.axes.get_xaxis().set_visible(False)
                    im.axes.get_yaxis().set_visible(False)
                else:
                    im.set_data(output_image)

                pyplot.savefig(os.path.join(output_dir, output_fn),
                               bbox_inches='tight', pad_inches=0)
                output_fns.append(output_fn)

            results.append({'input_file_name': inp['filename'],
                            'has_output': True,
                            'predict_probs': decoded_predictions[i],
                            'has_processed_input': False,
                            'output_file_names': output_fns})
        return results

    def get_logit_tensor(self):
        # Assume that the logits are the tensor input to the last softmax
        # operation in the computation graph
        sm = [node
              for node in self.model.sess.graph_def.node
              if node.name == self.model.tf_predict_var.name.split(':')[0]][-1]
        logit_op_name = sm.input[0]
        return self.model.sess.graph.get_tensor_by_name(
            '{}:0'.format(logit_op_name))
