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
from picasso.visualizations.base import BaseVisualization


class ClassProbabilities(BaseVisualization):
    """Display top class probabilities for a given image

    This is the simplest kind of visualization -- it merely displays the top
    class probabilities of the input image.

    """

    DESCRIPTION = 'Predict class probabilities from new examples'

    def make_visualization(self, inputs, output_dir):
        pre_processed_arrays = self.model.preprocess([example['data']
                                                      for example in inputs])
        predictions = self.model.sess.run(self.model.tf_predict_var,
                                          feed_dict={self.model.tf_input_var:
                                                     pre_processed_arrays})
        filtered_predictions = self.model.decode_prob(predictions)
        results = []
        for i, inp in enumerate(inputs):
            results.append({'input_file_name': inp['filename'],
                            'has_output': False,
                            'has_processed_input': False,
                            'predict_probs': filtered_predictions[i]})
        return results
