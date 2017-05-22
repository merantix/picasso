import os
import glob
import json
from datetime import datetime

import keras.backend as K
from keras.models import model_from_json,load_model

from picasso.ml_frameworks.tensorflow.model import TFModel


class KerasModel(TFModel):
    """Implements model loading functions for Keras

    Using this Keras module will require the h5py library,
    which is not included with Keras

    Attributes:
        sess (Tensorflow :obj:`Session`): underlying Tensorflow session of
            the Keras model.
        tf_predict_var (:obj:`Tensor`): tensorflow tensor which represents
            the class probabilities
        tf_input_var (:obj:`Tensor`): tensorflow tensor which represents
            the inputs

    """

    def load(self, data_dir='./'):

        """Load graph and weight data

        Args:
            data_dir (:obj:`str`): location of Keras checkpoint (`.hdf5`) files
                and model (in `.json`) structure.  The default behavior
                is to take the latest of each, by OS timestamp.

        """
        if int('keras.__version'[0]) == 1:
            # find newest ckpt and graph files
            try:
                latest_ckpt = max(glob.iglob(
                    os.path.join(data_dir, '*.h*5')),
                                  key=os.path.getctime)

                self.latest_ckpt_name = os.path.basename(latest_ckpt)
                self.latest_ckpt_time = str(datetime.fromtimestamp(
                    os.path.getmtime(latest_ckpt))
                )

            except ValueError:
                raise FileNotFoundError('No checkpoint (.hdf5 or .h5) files '
                                        'available at {}'.format(data_dir))
            try:
                latest_json = max(glob.iglob(os.path.join(data_dir, '*.json')),
                                  key=os.path.getctime)
            except ValueError:
                raise FileNotFoundError('No graph (.json) files '
                                        'available at {}'.format(data_dir))

            # for tensorflow compatibility
            K.set_learning_phase(0)
            with open(latest_json, 'r') as f:
                model_json = json.loads(f.read())
                self.model = model_from_json(model_json)

            self.model.load_weights(latest_ckpt)
            self.sess = K.get_session()

            self.tf_predict_var = self.model.outputs[0]
            self.tf_input_var = self.model.inputs[0]
        if int('keras.__version'[0]) == 2:
            try:
                latest_ckpt = max(glob.iglob(
                    os.path.join(data_dir, '*.h*5')),
                    key=os.path.getctime)

                self.latest_ckpt_name = os.path.basename(latest_ckpt)
                self.latest_ckpt_time = str(datetime.fromtimestamp(
                    os.path.getmtime(latest_ckpt))
                )

            except ValueError:
                raise FileNotFoundError('No checkpoint (.hdf5 or .h5) files '
                                        'available at {}'.format(data_dir))


            # for tensorflow compatibility
            K.set_learning_phase(0)
            self.keras=load_model(latest_ckpt)

            self.sess = K.get_session()

            self.tf_predict_var = self.model.outputs[0]
            self.tf_input_var = self.model.inputs[0]

    def _predict(self, input_array):
        return self.model.predict(input_array)
