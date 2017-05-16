"""Visualizations live here

All default and user-defined visualizations are submodules of this
module.  All classes defined in this directory (except BaseVisualization)
will be imported.

"""
import os
__all__ = [x.rpartition('.')[0] for x in os.listdir(__path__[0])
           if not x.startswith('__') and x.endswith('py')]


class BaseVisualization:
    """Template for visualizations

    Attributes:
        description (:obj:`str`): short description of the visualization
        model (instance of :class:`.ml_frameworks.model.Model` or derived class):
            backend to use
        settings (:obj:`dict`): a settings dictionary.  Settings defined
            here will be rendered in html for the user to select.  See
            derived classes for examples.
    """
    def __init__(self, model):
        self.model = model

    def make_visualization(self, inputs, output_dir, settings=None):
        """Generate the visualization

        All visualizations must implement this method.

        Args:
            inputs (iterable of :class:`PIL.Image`): images uploaded by the
                user.  Will have already been converted to :obj:`Image`
                objects.
            output_dir (:obj:`str`): a directory to store outputs (e.g. plots)

        Returns:
            data needed to render the visualization.  Since there is an
            associated HTML template, the return type is arbitrary.
        """
        raise NotImplementedError
