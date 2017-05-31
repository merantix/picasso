#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_picasso
----------------------------------

Tests for `picasso` module.
"""
import os

from flask import url_for
import pytest
from werkzeug.test import EnvironBuilder


class TestWebApp:
    from picasso.picasso import VISUALIZATON_CLASSES

    def test_landing_page_get(self, client):
        assert client.get(url_for('landing')).status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATON_CLASSES)
    def test_landing_page_post(self, client, vis):
        rv = client.post(url_for('landing'),
                         data=dict(choice=vis.__name__))
        assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATON_CLASSES)
    def test_settings_page(self, client, vis):
        if hasattr(vis, 'settings'):
            with client.session_transaction() as sess:
                sess['vis_name'] = vis.__name__
            rv = client.post(url_for('visualization_settings'))
            assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATON_CLASSES)
    def test_file_selection_get(self, client, vis):
        with client.session_transaction() as sess:
            sess['vis_name'] = vis.__name__
        rv = client.get(url_for('select_files'))
        assert rv.status_code == 200

    @pytest.mark.parametrize("vis", VISUALIZATON_CLASSES)
    def test_file_selection_post(self, client, vis, random_image_files):
        with client.session_transaction() as sess:
            sess['vis_name'] = vis.__name__
            # load some settings into the session if the visualization calls
            # for it
            if hasattr(vis, 'settings'):
                sess['settings'] = {key: vis.settings[key][0]
                                    for key in vis.settings}
            else:
                sess['settings'] = {}

        # random images
        builder = EnvironBuilder(path=url_for('select_files'), method='POST')
        for path in random_image_files.listdir():
            path = str(path)
            builder.files.add_file('file[]', path,
                                   filename=os.path.split(str(path))[-1])
        rv = client.post(url_for('select_files'), data=builder.files)
        assert rv.status_code == 200


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
        from picasso.ml_frameworks.keras.model import KerasModel

        data_path = os.path.join('picasso', 'examples',
                                 'keras', 'data-volume')

        km = KerasModel()
        km.load(data_path)

        temp = tempfile.mkdtemp()
        km.model.save(os.path.join(temp, 'temp.h5'))

        km = KerasModel()
        km.load(temp)

        assert km.tf_predict_var is not None


class TestTensorflowBackend:

    def test_tensorflow_backend(self, client, monkeypatch):
        """Only tests tensorflow backend loads without error

        """

        from picasso.ml_frameworks.tensorflow.model import TFModel
        data_path = os.path.join('picasso', 'examples',
                                 'tensorflow', 'data-volume')
        tfm = TFModel(tf_predict_var='Softmax:0',
                      tf_input_var='convolution2d_input_1:0')
        tfm.load(data_path)
        assert tfm.tf_predict_var is not None
        assert tfm.tf_input_var is not None
