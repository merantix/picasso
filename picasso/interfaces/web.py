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
    return render_template('index.html')

