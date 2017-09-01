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
import os
import json
from keras.applications.vgg16 import VGG16

path = 'data-volume'
try:
    os.mkdir(path)
except FileExistsError:
    pass

print('Downloading and setting up VGG16...')

vgg16 = VGG16()

print('Saving...')

if not os.path.exists(os.path.join(os.path.dirname(__file__), path)):
    os.makedirs(os.path.join(os.path.dirname(__file__), path))

with open(os.path.join(os.path.dirname(__file__),
                       path,
                       'vgg16.json'), 'w') as json_file:
    json.dump(vgg16.to_json(), json_file)

vgg16.save_weights(os.path.join(os.path.dirname(__file__),
                                path,
                                'vgg16.hdf5'))

print('Done.')
