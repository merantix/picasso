# -*- coding: utf-8 -*-
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

Attributes:
    APP_TITLE (:obj:`str`): Name of the application to display in the
        title bar
    VISUALIZATON_CLASSES(:obj:`tuple` of :class:`.BaseVisualization`):
        Visualization classes available for rendering.

"""
import os
import io
import time
import inspect
from operator import itemgetter
from tempfile import mkdtemp
from importlib import import_module
from types import ModuleType

from PIL import Image
from flask import (
    g,
    render_template,
    request,
    session,
    send_from_directory
)

from picasso import app
from picasso.ml_frameworks.model import generate_model
from picasso.visualizations import BaseVisualization
from picasso.visualizations import *

APP_TITLE = 'Picasso Visualizer'

# import visualizations classes dynamically
visualization_attr = vars(
    import_module('picasso.visualizations'))
visualization_submodules = [visualization_attr[x] for x in visualization_attr
                            if isinstance(visualization_attr[x], ModuleType)]
VISUALIZATON_CLASSES = []
for submodule in visualization_submodules:
    members = vars(submodule)
    classes = [members[x] for x in members if inspect.isclass(members[x]) and
               issubclass(members[x], BaseVisualization) and
               members[x] is not BaseVisualization]
    VISUALIZATON_CLASSES += classes

# Use a bogus secret key for debugging ease. No
# client information is stored, the secret key is only
# necessary for generating the session cookie.
if app.debug:
    app.secret_key = '...'
else:
    app.secret_key = os.urandom(24)

# This pattern is used in other projects with Flask and
# tensorflow, but probably isn't the most stable or
# safest way.  Would be much better to connect to a
# persistent tensorflow session running in another process or
# machine.
ml_backend = \
        generate_model(
            **{k.lower(): v for (k, v)
               in app.config.items()
               if k.startswith('BACKEND')}
        )
ml_backend.load(app.config['DATA_DIR'])


def get_visualizations():
    """Get visualization classes in context

    Puts the available visualizations in the request context
    and returns them.

    Returns:
        :obj:`list` of instances of :class:`.BaseVisualization` or
        derived class

    """
    if not hasattr(g, 'visualizations'):
        g.visualizations = {}
        for VisClass in VISUALIZATON_CLASSES:
            vis = VisClass(get_ml_backend())
            g.visualizations[vis.__class__.__name__] = vis

    return g.visualizations


def get_ml_backend():
    """Get machine learning backend in context

    Puts the backend in the request context and returns it.

    Returns:
        instance of :class:`.ml_frameworks.model.Model` or derived
        class
    """
    if not hasattr(g, 'ml_backend'):
        g.ml_backend = ml_backend
    return g.ml_backend


def get_app_state():
    """Get current status of application in context

    Returns:
        :obj:`dict` of application status

    """
    if not hasattr(g, 'app_state'):
        model = get_ml_backend()
        g.app_state = {
            'app_title': APP_TITLE,
            'backend': type(model).__name__,
            'latest_ckpt_name': model.latest_ckpt_name,
            'latest_ckpt_time': model.latest_ckpt_time
        }
    return g.app_state


@app.route('/', methods=['GET', 'POST'])
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
        if hasattr(vis, 'settings'):
            return visualization_settings()
        return select_files()

    # otherwise, on GET request
    visualizations = get_visualizations()
    vis_desc = [{'name': vis,
                 'description': visualizations[vis].description}
                for vis in visualizations]
    session.clear()
    return render_template('select_visualization.html',
                           app_state=get_app_state(),
                           visualizations=sorted(vis_desc,
                                                 key=itemgetter('name'))
                           )


@app.route('/visualization_settings', methods=['POST'])
def visualization_settings():
    """Visualization settings page

    Will only render if the visualization object has a `settings`
    attribute.

    """
    if request.method == 'POST':
        vis = get_visualizations()[session['vis_name']]
        return render_template('settings.html',
                               app_state=get_app_state(),
                               current_vis=session['vis_name'],
                               settings=vis.settings)


@app.route('/select_files', methods=['GET', 'POST'])
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
        session['img_output_dir'] = mkdtemp()
        output = \
            vis.make_visualization(inputs,
                                   output_dir=session['img_output_dir'],
                                   settings=session['settings'])
        duration = '{:.2f}'.format(time.time() - start_time, 2)

        for i, file_obj in enumerate(request.files.getlist('file[]')):
            output[i].update({'filename': file_obj.filename})

        temp_dir = mkdtemp()
        session['img_input_dir'] = temp_dir
        for entry in inputs:
            path = os.path.join(temp_dir, entry['filename'])
            entry['data'].save(path, 'PNG')

        kwargs = {}
        if hasattr(vis, 'reference_link'):
            kwargs.update({'reference_link': vis.reference_link})

        return render_template('{}.html'.format(session['vis_name']),
                               inputs=inputs,
                               results=output,
                               current_vis=session['vis_name'],
                               settings=session['settings'],
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


@app.route('/inputs/<filename>')
def download_inputs(filename):
    """For serving input images"""
    return send_from_directory(session['img_input_dir'],
                               filename)


@app.route('/outputs/<filename>')
def download_outputs(filename):
    """For serving output images"""
    return send_from_directory(session['img_output_dir'],
                               filename)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', app_state=get_app_state()), 500


@app.errorhandler(404)
def not_found_error(e):
    return render_template('404.html', app_state=get_app_state()), 404
