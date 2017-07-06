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
    VISUALIZATION_CLASSES (:obj:`tuple` of :class:`.BaseVisualization`):
        Visualization classes available for rendering.

"""
from importlib import import_module
import inspect
import io
import os
from operator import itemgetter
import shutil
from tempfile import mkdtemp
import time
from types import ModuleType

from PIL import Image
from flask import (
    g,
    render_template,
    request,
    session,
    send_from_directory,
    jsonify
)
from werkzeug.utils import secure_filename

from picasso import __version__
from picasso import app
from picasso.models.base import load_model
from picasso.visualizations import *
from picasso.visualizations.base import BaseVisualization

APP_TITLE = 'Picasso Visualizer'


def _get_visualization_classes():
    """Import visualizations classes dynamically

    """
    visualization_attr = vars(
        import_module('picasso.visualizations'))
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


VISUALIZATION_CLASSES = _get_visualization_classes()

# Use a bogus secret key for debugging ease. No client information is stored;
# the secret key is only necessary for generating the session cookie.
if app.debug:
    app.secret_key = '...'
else:
    app.secret_key = os.urandom(24)

# This pattern is used in other projects with Flask and Tensorflow, but
# but probably isn't the most stable or safest way.  Would be much better to
# connect to a persistent Tensorflow session running in another process or
# machine.
model = load_model(app.config['MODEL_CLS_PATH'], app.config['MODEL_CLS_NAME'],
                   app.config['MODEL_LOAD_ARGS'])


@app.before_request
def initialize_new_session():
    """Check session and initialize if necessary

    Before every request, check the user session.  If no session exists, add
    one and provide temporary locations for images

    """
    if 'image_uid_counter' in session and 'image_list' in session:
        app.logger.debug('images are already being tracked')
    else:
        # reset image list counter for the session
        session['image_uid_counter'] = 0
        session['image_list'] = []
    if 'img_input_dir' in session and 'img_output_dir' in session:
        app.logger.debug('temporary image directories already exist')
    else:
        # make image upload directory
        session['img_input_dir'] = mkdtemp()
        session['img_output_dir'] = mkdtemp()


def get_model():
    """Get the NN model that's being analyzed from the request context.  Put
    the model in the request context if it is not yet there.

    Returns:
        instance of :class:`.models.model.Model` or derived
        class
    """
    if not hasattr(g, 'model'):
        g.model = model
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
        for VisClass in VISUALIZATION_CLASSES:
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


@app.route('/api/', methods=['GET'])
def api_root():
    """The root of the REST API

    displays a hello world message.

    """
    return jsonify(message='Picasso {version}. '
                   'Developer documentation coming soon!'
                   .format(version=__version__),
                  version=__version__)


@app.route('/api/images', methods=['POST', 'GET'])
def api_images():
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
            app.logger.debug('File %d is saved as %s',
                             image['uid'],
                             image['filename'])
            session['image_list'].append(image)
            return jsonify(ok="true", file=image['filename'], uid=image['uid'])
        return jsonify(ok="false")
    if request.method == 'GET':
        return jsonify(images=session['image_list'])


@app.route('/api/visualize', methods=['GET'])
def api_visualize():
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
    output = vis.make_visualization(inputs,
                                    output_dir=session['img_output_dir'],
                                    settings=session['settings'])
    return jsonify(output=output)


@app.route('/api/reset', methods=['GET'])
def end_session():
    """Delete the session and clear temporary directories

    """
    shutil.rmtree(session['img_input_dir'])
    shutil.rmtree(session['img_output_dir'])
    session.clear()
    return jsonify(ok='true')


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


@app.route('/visualization_settings', methods=['POST'])
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
        output = vis.make_visualization(inputs,
                                        output_dir=session['img_output_dir'],
                                        settings=session['settings'])
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
