# -*- coding: utf-8 -*-
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
#    Jan Steinke - Restful API
###############################################################################
"""utiltiy code to provide the Flask server with information

This code only provides utility functions to access the backend.
"""
from types import ModuleType
from importlib import import_module
import inspect
from flask import (
    g,
    current_app
)
from picasso.visualizations.base import BaseVisualization
from picasso.models.base import load_model

APP_TITLE = 'Picasso Visualizer'


def _get_visualization_classes():
    """Import visualizations classes dynamically
    """
    visualization_attr = vars(import_module('picasso.visualizations'))
    visualization_submodules = [
        visualization_attr[x]
        for x in visualization_attr
        if isinstance(visualization_attr[x], ModuleType)]
    visualization_classes = []
    for submodule in visualization_submodules:
        attrs = vars(submodule)
        for attr_name in attrs:
            attr = attrs[attr_name]
            if (inspect.isclass(attr)
                and issubclass(attr, BaseVisualization)
                    and attr is not BaseVisualization):
                visualization_classes.append(attr)
    return visualization_classes


def get_model():
    """Get the NN model that's being analyzed from the request context.  Put
    the model in the request context if it is not yet there.

    Returns:
        instance of :class:`.models.model.Model` or derived
        class
    """
    if not hasattr(g, 'model'):
        g.model = load_model(current_app.config['MODEL_CLS_PATH'],
                             current_app.config['MODEL_CLS_NAME'],
                             current_app.config['MODEL_LOAD_ARGS'])
    return g.model


def get_visualizations():
    """Get the available visualizations from the request context.  Put the
    visualizations in the request context if they are not yet there.

    Returns:
        :obj:`list` of instances of :class:`.BaseVisualization` or
        derived class

    """
    if not hasattr(g, 'visualizations'):
        g.visualizations = {}
        for VisClass in _get_visualization_classes():
            vis = VisClass(get_model())
            g.visualizations[vis.__class__.__name__] = vis
    return g.visualizations


def get_app_state():
    """Get current status of application in context

    Returns:
        :obj:`dict` of application status

    """
    if not hasattr(g, 'app_state'):
        model = get_model()
        g.app_state = {
            'app_title': APP_TITLE,
            'model_name': type(model).__name__,
            'latest_ckpt_name': model.latest_ckpt_name,
            'latest_ckpt_time': model.latest_ckpt_time
        }
    return g.app_state
