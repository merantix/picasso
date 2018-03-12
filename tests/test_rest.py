import io
import json

import pytest
from flask import url_for
from PIL import Image, ImageChops


def verify_data(client, data, vis, prefix=''):
    res_path = './tests/resources/'
    assert data['input_file_name']
    assert data['predict_probs']
    if data['has_output']:
        assert data['output_file_names']
        i = 1
        for filename in data['output_file_names']:
            actual_image = client.get(url_for('api.download_outputs', filename=filename)).data
            actual_processed_input = Image.open(io.BytesIO(actual_image))
            expected_processed_input = Image.open(res_path + vis.__name__ + '/' + prefix + 'output/' + str(i) + '.png')
            assert ImageChops.difference(actual_processed_input, expected_processed_input).getbbox() is None
            i += 1
    if data['has_processed_input']:
        assert data['processed_input_file_name']
        filename = data['processed_input_file_name']
        actual_image = client.get(url_for('api.download_outputs', filename=filename)).data
        actual_processed_input = Image.open(io.BytesIO(actual_image))
        expected_processed_input = Image.open(res_path + vis.__name__ + '/' + prefix + 'pre/default.png')
        assert ImageChops.difference(actual_processed_input, expected_processed_input).getbbox() is None


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
        data = dict()
        data['file'] = (io.BytesIO(b), 'test.png')
        response = client.post(url_for('api.images'), data=data)
        data = json.loads(response.get_data(as_text=True))
        assert data['ok'] == 'true'
        assert type(data['file']) is str
        assert type(data['uid']) is int

    @pytest.mark.parametrize("vis", _get_visualization_classes())
    def test_api_visualizing_input(self, client, test_image, vis):
        upload_file = test_image
        with open(upload_file, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
        upload_data = dict()
        upload_data['file'] = (io.BytesIO(b), 'test.png')
        upload_response = client.post(url_for('api.images'), data=upload_data)
        upload_response_data = json.loads(upload_response.get_data(as_text=True))
        base_url = '{base}?visualizer={visualizer}&image={image}'.format(
            base=url_for('api.visualize'),
            visualizer=vis.__name__,
            image=str(upload_response_data['uid'])
        )
        settings_string = ''
        for setting in vis.ALLOWED_SETTINGS:
            settings_string += "&{0}={1}".format(setting, vis.ALLOWED_SETTINGS[setting][-1])

        default_response = client.get(base_url)
        assert default_response.status_code == 200
        raw_data_from_default_response = default_response.get_data(as_text=True)
        default_data = json.loads(raw_data_from_default_response)
        verify_data(client, default_data, vis)

        settings_response = client.get(base_url + settings_string)
        assert settings_response.status_code == 200
        raw_data_from_settings_response = settings_response.get_data(as_text=True)
        settings_data = json.loads(raw_data_from_settings_response)
        verify_data(client, settings_data, vis, prefix='settings_')

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
    def test_visualizers_information(self, client, vis):
        response = client.get(url_for('api.visualizers_information', vis_name=vis.__name__))
        assert response.status_code == 200
