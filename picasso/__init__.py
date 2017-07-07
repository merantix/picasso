# -*- coding: utf-8 -*-

__author__ = """Ryan Henderson"""
__email__ = 'ryan@merantix.com'
__version__ = 'v0.2.0'

from flask import Flask
import os
import sys

if sys.version_info.major < 3 or (sys.version_info.major == 3 and
                                  sys.version_info.minor < 5):
    raise SystemError('Python 3.5+ required, found {}'.format(sys.version))

app = Flask(__name__)
app.config.from_object('picasso.config.Default')

if os.getenv('PICASSO_SETTINGS'):
    app.config.from_envvar('PICASSO_SETTINGS')

deprecated_settings = ['BACKEND_PREPROCESSOR_NAME',
                       'BACKEND_PREPROCESSOR_PATH',
                       'BACKEND_POSTPROCESSOR_NAME',
                       'BACKEND_POSTPROCESSOR_PATH',
                       'BACKEND_PROB_DECODER_NAME',
                       'BACKEND_PROB_DECODER_PATH',
                       'DATA_DIR']

if any([x in app.config.keys() for x in deprecated_settings]):
    raise ValueError('It looks like you\'re using a deprecated'
                     ' setting.  The settings and utility functions'
                     ' have been changed as of version v0.2.0 (and '
                     'you\'re using {}). Changing to the updated '
                     ' settings is trivial: see '
                     'https://picasso.readthedocs.io/en/latest/models.html'
                     ' and '
                     'https://picasso.readthedocs.io/en/latest/settings.html'
                     .format(__version__))

import picasso.picasso
