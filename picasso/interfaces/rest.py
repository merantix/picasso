# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2017 Merantix GmbH
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Jan Steinke - Restful API
###############################################################################
"""Flask blueprint for accessing and manipulating image ressources

This is used by the main flask application to provide a REST API.
"""

import os
import shutil
from PIL import Image
from werkzeug.utils import secure_filename
from flask import (
    Blueprint,
    current_app,
    jsonify,
    session,
    request
    )
from picasso import __version__
from picasso.utils import get_visualizations

API = Blueprint('api', __name__)


@API.route('/', methods=['GET'])
def root():
    """The root of the REST API

    displays a hello world message.

    """
    return jsonify(message='Picasso {version}. '
                   'See API documentation at: '
                   'https://picasso.readthedocs.io/en/latest/api.html'
                   .format(version=__version__),
                   version=__version__)


@API.route('/images', methods=['POST', 'GET'])
def images():
    """Upload images via REST interface

    Check if file upload was successful and sanatize user input.

    TODO: return file URL instead of filename

    """
    if request.method == 'POST':
        file_upload = request.files['file']
        if file_upload:
            image = {}
            image['filename'] = secure_filename(file_upload.filename)
            full_path = os.path.join(session['img_input_dir'],
                                     image['filename'])
            file_upload.save(full_path)
            image['uid'] = session['image_uid_counter']
            session['image_uid_counter'] += 1
            current_app.logger.debug('File %d is saved as %s',
                                     image['uid'],
                                     image['filename'])
            session['image_list'].append(image)
            return jsonify(ok="true", file=image['filename'], uid=image['uid'])
        return jsonify(ok="false")
    if request.method == 'GET':
        return jsonify(images=session['image_list'])


@API.route('/visualizers', methods=['GET'])
def visualizers():
    """Get a list of available visualizers

    Responses with a JSON list of available visualizers

    """
    list_of_visualizers = []
    for visualizer in get_visualizations():
        list_of_visualizers.append({'name': visualizer})
    return jsonify(visualizers=list_of_visualizers)


@API.route('/visualizers/<vis_name>', methods=['GET'])
def visualizers_information(vis_name):
    vis = get_visualizations()[vis_name]
    if hasattr(vis, 'ALLOWED_SETTINGS'):
        settings = vis.ALLOWED_SETTINGS
    else:
        settings = {}

    return jsonify(settings=settings)


@API.route('/visualize', methods=['GET'])
def visualize():
    """Trigger a visualization via the REST API

    Takes a single image and generates the visualization data, returning the
    output exactly as given by the target visualization.

    """

    session['settings'] = {}
    image_uid = request.args.get('image')
    vis_name = request.args.get('visualizer')
    vis = get_visualizations()[vis_name]
    if hasattr(vis, 'settings'):
        for key in vis.settings.keys():
            if request.args.get(key) is not None:
                session['settings'][key] = request.args.get(key)
            else:
                session['settings'][key] = vis.settings[key][0]
    inputs = []
    for image in session['image_list']:
        if image['uid'] == int(image_uid):
            full_path = os.path.join(session['img_input_dir'],
                                     image['filename'])
            entry = {}
            entry['filename'] = image['filename']
            entry['data'] = Image.open(full_path)
            inputs.append(entry)
    if 'settings' in session:
        vis.update_settings(session['settings'])
    output = vis.make_visualization(
        inputs, output_dir=session['img_output_dir'])
    return jsonify(output[0])


@API.route('/reset', methods=['GET'])
def reset():
    """Delete the session and clear temporary directories

    """
    shutil.rmtree(session['img_input_dir'])
    shutil.rmtree(session['img_output_dir'])
    session.clear()
    return jsonify(ok='true')
