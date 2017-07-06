from picasso.visualizations.base import BaseVisualization


class ClassProbabilities(BaseVisualization):
    """Display top class probabilities for a given image

    This is the simplest kind of visualization -- it merely displays the top
    class probabilities of the input image.

    """

    DESCRIPTION = 'Predict class probabilities from new examples'

    def make_visualization(self, inputs, output_dir, settings=None):
        pre_processed_arrays = self.model.preprocess([example['data']
                                                      for example in inputs])
        predictions = self.model.sess.run(self.model.tf_predict_var,
                                          feed_dict={self.model.tf_input_var:
                                                     pre_processed_arrays})
        filtered_predictions = self.model.decode_prob(predictions)
        results = []
        for i, inp in enumerate(inputs):
            results.append({'input_file_name': inp['filename'],
                            'predict_probs': filtered_predictions[i]})
        return results
