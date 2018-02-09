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
#    Josh Chen - refactor and class config
#    Jan Steinke - Restful API
#    XdpAreKid - Support Keras >= 2
###############################################################################
"""Flask server code for visualization

This is the entry point for the application. All views and
logic for the webapp are laid out here.

Examples:
    To run using the Flask server (from the parent directory)::

        $ export FLASK_APP=picasso
        $ flask run

    This will start the app with the default settings (using the
    Keras backend and a convolutional MNIST digits classifier).

    To use a custom configuration, set an environment variable
    to point to it like this::

        $ export PICASSO_SETTINGS=/path/to/the/config.py

"""
import io
import os
import logging
from operator import itemgetter
from tempfile import mkdtemp
import time

from PIL import Image
from flask import (
    render_template,
    request,
    session,
    send_from_directory,
    Blueprint,
    current_app)

from picasso.models.base import load_model
from picasso.visualizations import *
from picasso.utils import (
    get_app_state,
    get_visualizations
)

# This pattern is used in other projects with Flask and Tensorflow, but
# but probably isn't the most stable or safest way.  Would be much better to
# connect to a persistent Tensorflow session running in another process or
# machine.
# model = load_model(current_app.config['MODEL_CLS_PATH'], current_app.config['MODEL_CLS_NAME'],
#                    current_app.config['MODEL_LOAD_ARGS'])

frontend = Blueprint('picasso', __name__)
logger = logging.getLogger(__name__)


@frontend.before_request
def initialize_new_session():
    """Check session and initialize if necessary

    Before every request, check the user session.  If no session exists, add
    one and provide temporary locations for images

    """
    if 'image_uid_counter' in session and 'image_list' in session:
        logger.debug('images are already being tracked')
    else:
        # reset image list counter for the session
        session['image_uid_counter'] = 0
        session['image_list'] = []
    if 'img_input_dir' in session and 'img_output_dir' in session:
        logger.debug('temporary image directories already exist')
    else:
        # make image upload directory
        session['img_input_dir'] = mkdtemp()
        session['img_output_dir'] = mkdtemp()


@frontend.route('/', methods=['GET', 'POST'])
def landing():
    """Landing page for the application

    If the request is `GET`, render the landing page.  If
    `POST`, then store the visualization in the session and
    render the visualization settings page (if applicable) or
    render file selection.

    """
    if request.method == 'POST':
        session['vis_name'] = request.form.get('choice')
        vis = get_visualizations()[session['vis_name']]
        if vis.ALLOWED_SETTINGS:
            return visualization_settings()
        return select_files()

    # otherwise, on GET request
    visualizations = get_visualizations()
    vis_desc = [{'name': vis,
                 'description': visualizations[vis].DESCRIPTION}
                for vis in visualizations]
    session.clear()
    return render_template('select_visualization.html',
                           app_state=get_app_state(),
                           visualizations=sorted(vis_desc,
                                                 key=itemgetter('name')))


@frontend.route('/visualization_settings', methods=['POST'])
def visualization_settings():
    """Visualization settings page

    Will only render if the visualization object has a non-null
    `ALLOWED_SETTINGS` attribute.

    """
    if request.method == 'POST':
        vis = get_visualizations()[session['vis_name']]
        return render_template('settings.html',
                               app_state=get_app_state(),
                               current_vis=session['vis_name'],
                               settings=vis.ALLOWED_SETTINGS)


@frontend.route('/select_files', methods=['GET', 'POST'])
def select_files():
    """File selection and final display of visualization

    If the request contains no files, then render the file
    selection page.  Otherwise render the visualization.

    Todo:
        Logically, this route should be split into `select_files`
        and `result`.

    """
    if 'file[]' in request.files:
        vis = get_visualizations()[session['vis_name']]
        inputs = []
        for file_obj in request.files.getlist('file[]'):
            entry = {}
            entry.update({'filename': file_obj.filename})
            # Why is this necessary? Unsure why Flask sometimes
            # sends the files as bytestreams vs. strings.
            try:
                entry.update({'data':
                    Image.open(
                        io.BytesIO(file_obj.stream.getvalue())
                    )})
            except AttributeError:
                entry.update({'data':
                    Image.open(
                        io.BytesIO(file_obj.stream.read())
                    )})
            inputs.append(entry)

        start_time = time.time()
        if 'settings' in session:
            vis.update_settings(session['settings'])
        output = vis.make_visualization(inputs,
                                        output_dir=session['img_output_dir'])
        duration = '{:.2f}'.format(time.time() - start_time, 2)

        for i, file_obj in enumerate(request.files.getlist('file[]')):
            output[i].update({'filename': file_obj.filename})

        for entry in inputs:
            path = os.path.join(session['img_input_dir'], entry['filename'])
            entry['data'].save(path, 'PNG')

        kwargs = {}
        if vis.REFERENCE_LINK:
            kwargs['reference_link'] = vis.REFERENCE_LINK

        return render_template('{}.html'.format(session['vis_name']),
                               inputs=inputs,
                               results=output,
                               current_vis=session['vis_name'],
                               app_state=get_app_state(),
                               duration=duration,
                               **kwargs)

    # otherwise, if no files in request
    session['settings'] = request.form.to_dict()
    if 'choice' in session['settings']:
        session['settings'].pop('choice')
    return render_template('select_files.html',
                           app_state=get_app_state(),
                           current_vis=session['vis_name'],
                           settings=session['settings'])



