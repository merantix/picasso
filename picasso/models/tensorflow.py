from datetime import datetime
import glob
import os

import tensorflow as tf

from picasso.models.base import BaseModel


class TFModel(BaseModel):
    """Implements model loading functions for Tensorflow.

    """

    def load(self, data_dir, tf_input_var=None, tf_predict_var=None):
        """Load graph and weight data.

        Args:
            data_dir (:obj:`str`): location of tensorflow checkpoint data.
                We'll need the .meta file to reconstruct the graph and the data
                (checkpoint) files to fill in the weights of the model.  The
                default behavior is take the latest files, by OS timestamp.
            tf_input_var (:obj:`str`): Name of the tensor corresponding to the
                model's inputs.  You must define this if you are loading the
                model from a checkpoint.
            tf_predict_var (:obj:`str`): Name of the tensor corresponding to
                the model's predictions.  You must define this if you are
                loading the model from a checkpoint.

        """
        # find newest ckpt and meta files
        try:
            latest_ckpt_fn = max(
                filter(
                    # exclude index and meta files which may have earlier
                    # timestamps
                    lambda x: os.path.splitext(x)[-1].startswith('.meta') or
                    os.path.splitext(x)[-1].startswith('.index'),
                    glob.glob(os.path.join(data_dir, '*.ckpt*'))),
                key=os.path.getctime)
            latest_ckpt_time = str(
                datetime.fromtimestamp(os.path.getmtime(latest_ckpt_fn)))
            # remove any step info that's been appended to the extension
            fileext_div = latest_ckpt_fn.rfind('.ckpt')
            additional_ext = latest_ckpt_fn.rfind('.', fileext_div + 1)
            if additional_ext < 0:
                latest_ckpt = latest_ckpt_fn
            else:
                latest_ckpt = latest_ckpt_fn[:additional_ext]
        except ValueError:
            raise FileNotFoundError('No checkpoint (.ckpt) files '
                                    'available at {}'.format(data_dir))

        try:
            latest_meta = max(glob.iglob(os.path.join(data_dir, '*.meta')),
                              key=os.path.getctime)
        except ValueError:
            raise FileNotFoundError('No graph (.meta) files '
                                    'available at {}'.format(data_dir))

        self._sess = tf.Session()
        self._sess.as_default()

        self._saver = tf.train.import_meta_graph(latest_meta)
        self._saver.restore(self._sess, latest_ckpt)

        self._tf_input_var = self._sess.graph.get_tensor_by_name(tf_input_var)
        self._tf_predict_var = self._sess.graph.get_tensor_by_name(
            tf_predict_var)
        self._model_name = type(self).__name__
        self._latest_ckpt_name = latest_ckpt_fn
        self._latest_ckpt_time = latest_ckpt_time

    def predict(self, input_array):
        return self.sess.run(self.tf_predict_var,
                             {self.tf_input_var: input_array})
