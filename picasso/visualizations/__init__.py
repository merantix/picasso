"""Visualizations live here

All default and user-defined visualizations are submodules of this
module.  All classes defined in this directory (except BaseVisualization)
will be imported.

"""
import os

__all__ = [x.rpartition('.')[0] for x in os.listdir(__path__[0])
           if not x.startswith('__') and x.endswith('py')]
