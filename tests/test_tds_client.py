import logging
import os

import pytest
import requests

from aviso_client.tds_client import http_download


def test_http_download(mocker, tmp_path):
    fake_data = b'fake file contents'

    test_url = 'https://fake-server.com/data/file1.nc'
    filename = os.path.basename(test_url)
    expected_path = tmp_path / filename
    fake_response = mocker.MagicMock()
    fake_response.content = fake_data
    fake_response.raise_for_status.return_value = None

    mocker.patch('requests.get', return_value=fake_response)

    mocker.patch('aviso_client.auth.ensure_credentials',
                 return_value=('user', 'pass'))

    with pytest.raises(FileNotFoundError):
        http_download(test_url, 'bad_path')

    result_path = http_download(test_url, tmp_path)

    assert os.path.exists(result_path)
    assert result_path == str(expected_path)

    with open(result_path, 'rb') as f:
        assert f.read() == fake_data


def test_http_download_error_msg(mocker, tmp_path, caplog):
    url = 'https://bad_url'

    fake_response = mocker.MagicMock()
    fake_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        '404 Client Error')

    mocker.patch('requests.get', return_value=fake_response)
    mocker.patch('aviso_client.auth.ensure_credentials',
                 return_value=('user', 'pass'))
    mocked_logger = mocker.patch('aviso_client.tds_client.logger')

    result = http_download(url, tmp_path)
    mocked_logger.error.assert_called_once()
    assert result is None
