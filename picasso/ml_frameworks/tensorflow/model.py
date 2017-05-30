import os
import glob
from datetime import datetime

import tensorflow as tf

from picasso.ml_frameworks.model import Model


class TFModel(BaseModel):
    """Implements model loading functions for Tensorflow.
    
    """

    # Name of the tensor corresponding to the model's inputs.  You must define
    # this if you are loading the model from a checkpoint.
    TF_INPUT_VAR = None

    # Name of the tensor corresponding to the model's inputs.  You must define
    # this if you are loading the model from a checkpoint.
    TF_PREDICT_VAR = None

    def _load(self, data_dir):
        """Load graph and weight data

        Args:
            data_dir (:obj:`str`): location of tensorflow checkpoint data.
                We'll need the .meta file to reconstruct the graph and the data
                (checkpoint) files to fill in the weights of the model.  The
                default behavior is take the latest files, by OS timestamp.

        """
        self._sess = tf.Session()
        self._sess.as_default()

        # find newest ckpt and meta files
        try:
            latest_ckpt_fn = max(glob.iglob(os.path.join(data_dir, '*.ckpt*')),
                                 key=os.path.getctime)
            self._latest_ckpt_time = str(
                datetime.fromtimestamp(os.path.getmtime(latest_ckpt_fn)))
        except ValueError:
            raise FileNotFoundError('No checkpoint (.ckpt) files '
                                    'available at {}'.format(data_dir))
        latest_ckpt = latest_ckpt_fn[:latest_ckpt_fn.rfind('.ckpt') + 5]

        try:
            latest_meta = max(glob.iglob(os.path.join(data_dir, '*.meta')),
                              key=os.path.getctime)
        except ValueError:
            raise FileNotFoundError('No graph (.meta) files '
                                    'available at {}'.format(data_dir))

        self._saver = tf.train.import_meta_graph(latest_meta)
        self._saver.restore(self._sess, latest_ckpt)

        self._tf_input_var = self.sess.graph.get_tensor_by_name(
            self.TF_INPUT_VAR)
        self._tf_predict_var = self._sess.graph.get_tensor_by_name(
            self.TF_PREDICT_VAR)

    @property
    def description(self):
        return "%s loaded from %s (timestamp: %s)" % (
            type(self).__name__,
            self._data_dir,
            self._latest_ckpt_time)

    def predict(self, input_array):
        return self.sess.run(self.tf_predict_var,
                             {self.tf_input_var: input_array})
