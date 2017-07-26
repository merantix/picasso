#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_picasso
----------------------------------

Tests for `picasso` module.
"""
import io
import json
import os

from flask import url_for
import pytest
from werkzeug.test import EnvironBuilder


class TestWebApp:
    from picasso.picasso import VISUALIZATION_CLASSES

    def test_landing_page_get(self, client):
        assert client.get(url_for('landing')).status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATION_CLASSES)
    def test_landing_page_post(self, client, vis):
        rv = client.post(url_for('landing'),
                         data=dict(choice=vis.__name__))
        assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATION_CLASSES)
    def test_settings_page(self, client, vis):
        if hasattr(vis, 'settings'):
            with client.session_transaction() as sess:
                sess['vis_name'] = vis.__name__
            rv = client.post(url_for('visualization_settings'))
            assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATION_CLASSES)
    def test_file_selection_get(self, client, vis):
        with client.session_transaction() as sess:
            sess['vis_name'] = vis.__name__
        rv = client.get(url_for('select_files'))
        assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATION_CLASSES)
    def test_file_selection_post(self, client, vis, random_image_files):
        with client.session_transaction() as sess:
            sess['vis_name'] = vis.__name__
            # load some settings into the session if the visualization calls
            # for it
            if hasattr(vis, 'settings'):
                sess['settings'] = {key: vis.settings[key][0]
                                    for key in vis.settings}

        # random images
        builder = EnvironBuilder(path=url_for('select_files'), method='POST')
        for path in random_image_files.listdir():
            path = str(path)
            builder.files.add_file('file[]', path,
                                   filename=os.path.split(str(path))[-1])
        rv = client.post(url_for('select_files'), data=builder.files)
        assert rv.status_code == 200


class TestRestAPI:
    from picasso.picasso import VISUALIZATION_CLASSES

    def test_api_root_get(self, client):
        assert client.get(url_for('api_root')).status_code == 200

    def test_api_uploading_file(self, client, random_image_files):
        upload_file = str(random_image_files.listdir()[0])
        with open(upload_file, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
        data = {}
        data['file'] = (io.BytesIO(b), 'test.png')
        response = client.post(url_for('api_images'), data=data)
        data = json.loads(response.get_data(as_text=True))
        assert data['ok'] == 'true'
        assert type(data['file']) is str
        assert type(data['uid']) is int

    @pytest.mark.parametrize("vis", VISUALIZATION_CLASSES)
    def test_api_visualizing_input(self, client, random_image_files, vis):
        upload_file = str(random_image_files.listdir()[0])
        with open(upload_file, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
        data = {}
        data['file'] = (io.BytesIO(b), 'test.png')
        upl_response = client.post(url_for('api_images'), data=data)
        upl_data = json.loads(upl_response.get_data(as_text=True))
        response = client.get(url_for('api_visualize') + '?visualizer=' +
                              vis.__name__ +
                              '&image=' + str(upl_data['uid']))
        assert response.status_code == 200

    def test_listing_images(self, client):
        response = client.get(url_for('api_images'))
        assert response.status_code == 200

    def test_end_session(self, client):
        response = client.get(url_for('end_session'))
        assert response.status_code == 200


class TestBaseModel:

    def test_decode_prob(self, base_model, example_prob_array):
        results = base_model.decode_prob(example_prob_array)
        for i, result in enumerate(results):
            max_val = max(example_prob_array[i])
            assert result[0]['prob'] == '{:.3f}'.format(max_val)
            assert result[0]['index'] == example_prob_array[i].argmax()
            assert result[0]['name'] == str(result[0]['index'])


class TestKerasModel:

    def test_saved_model(self):
        # tests that KerasModel can load from a saved model
        import tempfile
        from picasso.models.keras import KerasModel

        data_path = os.path.join('picasso', 'examples',
                                 'keras', 'data-volume')

        km = KerasModel()
        km.load(data_path)

        temp = tempfile.mkdtemp()
        km._model.save(os.path.join(temp, 'temp.h5'))

        km = KerasModel()
        km.load(temp)

        assert km.tf_predict_var is not None


class TestTensorflowBackend:

    def test_tensorflow_backend(self, tensorflow_model):
        """Only tests tensorflow backend loads without error

        """
        tensorflow_model.load(
            data_dir=os.path.join('picasso', 'examples', 'tensorflow',
                                  'data-volume'),
            tf_predict_var='Softmax:0',
            tf_input_var='convolution2d_input_1:0')
        assert tensorflow_model.tf_predict_var is not None
        assert tensorflow_model.tf_input_var is not None
