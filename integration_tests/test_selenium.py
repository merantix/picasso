#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2017 Merantix GmbH
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Jan Steinke - Selenium integration tests
###############################################################################

"""
test_selenium
----------------------------------

Integration tests for `picasso` module.
"""

import pytest
from flask import url_for


@pytest.mark.usefixtures('live_server')
class TestIntegration:

    def test_page_load(self, webdriver):
        url = url_for('frontend.index', _external=True)
        webdriver.get(url)
        webdriver.find_element_by_id('appstate_checkpoint')


