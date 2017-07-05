"""Visualizations live here

All default and user-defined visualizations are submodules of this
module.  All classes defined in this directory (except BaseVisualization)
will be imported.

"""
import os
__all__ = [x.rpartition('.')[0] for x in os.listdir(__path__[0])
           if not x.startswith('__') and x.endswith('py')]


class BaseVisualization:
    """Interface encapsulating a NN visualization.

    This interface defines how a visualization is computed for a given NN
    model.

    """
    # (:obj:`str`): Short description of the visualization.
    DESCRIPTION = None

    # (:obj:`str`): Optional link to the paper specifying the visualization.
    REFERENCE_LINK = None

    # (:obj:`dict`): Optional visuzalization settings that the user can select.
    # Should be a dict mapping setting names to lists of their allowed values.
    ALLOWED_SETTINGS = None

    def __init__(self, model):
        """Create a new instance of this visualization.

        `BaseVisualization` is an interface and should only be instantiated via
        a subclass.

        Args:
            model (:obj:`.ml_frameworks.model.BaseModel`): NN model to be
                visualized.

        """
        self._model = model

    @property
    def model(self):
        """NN model to be visualized.

        (:obj:`.ml_frameworks.model.BaseModel`)

        """
        return self._model

    def make_visualization(self, inputs, output_dir, settings=None):
        """Generate the visualization.

        All visualizations must implement this method.

        Args:
            inputs (iterable of :class:`PIL.Image`): Batch of input images to
                make visualizations for, as PIL :obj:`Image` objects.
            output_dir (:obj:`str`): A directory to write outputs (e.g.,
                plots) to.

        Returns:
            data needed to render the visualization.  Since there is an
            associated HTML template, the return type is arbitrary.

        """
        raise NotImplementedError
