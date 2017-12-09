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
###############################################################################
from PIL import Image
import numpy as np
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from picasso import create_app


@pytest.fixture
def app():
    _app = create_app()
    return _app


@pytest.fixture(scope='module')
def webdriver():
    options = Options()
    options.add_argument('-headless')
    driver = Firefox(firefox_options=options)
    yield driver
    driver.quit()
