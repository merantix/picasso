# -*- coding: utf-8 -*-

__author__ = """Ryan Henderson"""
__email__ = 'ryan@merantix.com'
__version__ = 'v0.1.2'

from flask import Flask
import os
import sys

if sys.version_info.major < 3 or (sys.version_info.major == 3 and
                                  sys.version_info.minor < 5):
    raise SystemError('Python 3.5+ required, found {}'.format(sys.version))

app = Flask(__name__)
app.config.from_object('picasso.settings.Default')

if os.getenv('PICASSO_SETTINGS'):
    app.config.from_envvar('PICASSO_SETTINGS')

import picasso.picasso
