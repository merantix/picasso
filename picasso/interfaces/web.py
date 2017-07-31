# -*- coding: utf-8 -*-
"""Flask blueprint for interfacing with picasso via web.

This is used by the main flask application to provide a web front-end based on the REST api.
"""

from flask import (
    render_template,
    Blueprint
    )

frontend = Blueprint('frontend', __name__)


@frontend.route('/')
def index():
    return render_template('v2/index.html')

