import os
import glob
from datetime import datetime

import tensorflow as tf

from picasso.ml_frameworks.model import Model


class TFModel(Model):
    """Implements model loading functions for tensorflow"""

    def load(self, data_dir='./'):
        """Load graph and weight data

        Args:
            data_dir (:obj:`str`): location of tensorflow checkpoint
                data.  We'll need the .meta file to reconstruct
                the graph and the data (checkpoint) files to
                fill in the weights of the model.  The default
                behavior is take the latest files, by OS timestamp.

        """

        self.sess = tf.Session()
        self.sess.as_default()
        # find newest ckpt and meta files
        try:
            latest_ckpt_fn = max(
                filter(
                    # exclude index and meta files which may have earlier
                    # timestamps
                    lambda x: os.path.splitext(x)[-1].startswith('.meta') or
                    os.path.splitext(x)[-1].startswith('.index'),
                    glob.glob(os.path.join(data_dir, '*.ckpt*'))
                ),
                key=os.path.getctime)
            self.latest_ckpt_time = str(datetime.fromtimestamp(
                os.path.getmtime(latest_ckpt_fn)
            ))
            # remove any step info that's been appended to the
            # extenstion
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

        with self.sess.as_default() as sess:
            self.saver = tf.train.import_meta_graph(latest_meta)
            self.saver.restore(sess, latest_ckpt)

        self.tf_predict_var = \
            self.sess.graph.get_tensor_by_name(self.tf_predict_var)
        self.tf_input_var = \
            self.sess.graph.get_tensor_by_name(self.tf_input_var)

    def _predict(self, input_array):
        return self.sess.run(self.tf_predict_var,
                             {self.tf_input_var: input_array})
