import importlib
from operator import itemgetter
import warnings


def get_model(model_cls_path, model_cls_name, data_dir, **kwargs):
    """Get an instance of the described model.

    Args:
        model_cls_path: Path to the module in which the model class
            is defined.
        model_cls_name: Name of the model class.
        data_dir: Directory containing the graph and weights.
        kwargs: Arbitrary keyword arguments passed to the model's
            constructor.

    Returns:
        An instance of :class:`.ml_frameworks.model.BaseModel` or subclass

    """
    spec = importlib.util.spec_from_file_location('active_model',
                                                  model_cls_path)
    model_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_module)
    model_cls = getattr(model_module, model_cls_name)
    model = model_cls(data_dir, **kwargs)
    if not isinstance(model, BaseModel):
        warnings.warn("Loaded model '%s' at '%s' is not an instance of %r"
                      % (model_cls_name, model_cls_path, BaseModel))
    return model


class BaseModel:
    """Interface encapsulating a trained NN model usable for prediction.

    This interface defines:

      - How to load the model's topology and parameters from disk
      - How to preprocess a batch of examples for the model
      - How to perform prediction using the model
      - Etc

    """

    def __init__(self,
                 data_dir,
                 top_probs=5,
                 **kwargs):
        """Create a new instance of this model.
        
        `BaseModel` is an interface and should only be instantiated via a
        subclass.

        Args:
            top_probs (int): Number of classes to display per result. For
                instance, VGG16 has 1000 classes, we don't want to display a
                visualization for every single possibility.  Defaults to 5.
            kwargs: Arbitrary keyword arguments, useful for passing specific
                settings to derived classes.

        """
        self._data_dir = data_dir
        self._load(data_dir)

        self.top_probs = top_probs

    def _load(self, data_dir):
        """Load the model's graph and parameters from disk, and restore the
        model so that it can be run for inference.

        Args:
            data_dir (:obj:`str`): Full path to directory containing
                graph and weight data.

        """
        raise NotImplementedError

    @property
    def description(self):
        """A description of the loaded model.

        This description is rendered to the user in the UI.

        """
        return "%s loaded from %s" % (type(self).__name__, self._data_dir)

    @property
    def sess(self):
        """A Tensorflow session that can be used to evaluate tensors in the
        model.

        (:obj:`tf.Session`)

        """
        return self._sess

    @property
    def tf_input_var(self):
        """The Tensorflow tensor that represents the model's inputs.

        (:obj:`tf.Tensor`)

        """
        return self._tf_input_var

    @property
    def tf_predict_var(self):
        """The Tensorflow tensor that represents the model's predicted class
        probabilities.

        (:obj:`tf.Tensor`)

        """
        return self._tf_predict_var

    def preprocess(self, raw_inputs):
        """Preprocess raw inputs into the format required by the model.

        E.g, the raw image may need to converted to a numpy array of the
        appropriate dimension.

        By default, we perform no preprocessing.

        Args:
            raw_inputs (:obj:`list` of :obj:`PIL.Image`): List of raw
                input images of any mode and shape.

        Returns:
            array (float32): Images ready to be fed into the model.

        """
        return raw_inputs

    def predict(self, inputs):
        """Given preprocessed inputs, generate class probabilities by using the
        model to perform inference.

        Given an iterable of examples or numpy array where the first
        dimension is the number of example, return a n_examples x
        n_classes array of class predictions

        Args:
            inputs: Iterable of examples (e.g., a numpy array whose first
                dimension is the batch size).

        Returns:
            Class probabilities for each input example, as a numpy array of
            shape (num_examples, num_classes).

        """
        raise NotImplementedError

    def decode_prob(self, output_arr):
        """Given predicted class probabilites for a set of examples, annotate
        each logit with a class name.

        By default, we name each class using its index in the logits array.

        Args:
            output_arr (array): Class probabilities as output by
                `self.predict`, i.e., a numpy array of shape (num_examples,
                num_classes).

        Returns:
            Annotated class probabilities for each input example, as a list of
            dicts where each dict is formatted as:
                {
                    'index': class_index,
                    'name': class_name,
                    'prob': class_probability
                }

        """
        results = []
        for row in output_arr:
            entries = []
            for i, prob in enumerate(row):
                entries.append({'index': i,
                                'name': str(i),
                                'prob': prob})

            entries = sorted(entries,
                             key=itemgetter('prob'),
                             reverse=True)[:self.top_probs]

            for entry in entries:
                entry['prob'] = '{:.3f}'.format(entry['prob'])
            results.append(entries)
        return results
