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
"""Visualizations live here

All default and user-defined visualizations are submodules of this
module.  All classes defined in this directory (except BaseVisualization)
will be imported.

"""
import os

__all__ = [x.rpartition('.')[0] for x in os.listdir(__path__[0])
           if not x.startswith('__') and x.endswith('py')]
