import io
import json

import pytest
from flask import url_for


class TestRestAPI:
    from picasso.utils import _get_visualization_classes

    def test_api_root_get(self, client):
        assert client.get(url_for('api.root')).status_code == 200

    def test_api_get_app_state(self, client):
        response = client.get(url_for('api.app_state'))
        data = json.loads(response.get_data(as_text=True))
        assert data['app_title']
        assert data['latest_ckpt_name']
        assert data['latest_ckpt_time']
        assert data['model_name']

    def test_api_uploading_file(self, client, random_image_files):
        upload_file = str(random_image_files.listdir()[0])
        with open(upload_file, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
        data = {}
        data['file'] = (io.BytesIO(b), 'test.png')
        response = client.post(url_for('api.images'), data=data)
        data = json.loads(response.get_data(as_text=True))
        assert data['ok'] == 'true'
        assert type(data['file']) is str
        assert type(data['uid']) is int

    @pytest.mark.parametrize("vis", _get_visualization_classes())
    def test_api_visualizing_input(self, client, random_image_files, vis):
        upload_file = str(random_image_files.listdir()[0])
        with open(upload_file, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
        data = {}
        data['file'] = (io.BytesIO(b), 'test.png')
        upl_response = client.post(url_for('api.images'), data=data)
        upl_data = json.loads(upl_response.get_data(as_text=True))
        response = client.get(url_for('api.visualize') + '?visualizer=' +
                              vis.__name__ +
                              '&image=' + str(upl_data['uid']))
        raw_data = response.get_data(as_text=True)
        data = json.loads(raw_data)
        assert response.status_code == 200
        assert data['input_file_name']
        assert data['predict_probs']
        if data['has_output']:
            assert data['output_file_names']
        if data['has_processed_input']:
            assert data['processed_input_file_name']

    def test_listing_images(self, client):
        response = client.get(url_for('api.images'))
        assert response.status_code == 200

    def test_end_session(self, client):
        response = client.get(url_for('api.reset'))
        assert response.status_code == 200

    def test_visualizers(self, client):
        response = client.get(url_for('api.visualizers'))
        assert response.status_code == 200

    @pytest.mark.parametrize("vis", _get_visualization_classes())
    def test_visualizers_informations(self, client, vis):
        response = client.get(url_for('api.visualizers_information', vis_name=vis.__name__))
        assert response.status_code == 200