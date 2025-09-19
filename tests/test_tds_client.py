import logging
import os

import pytest

from aviso_client.tds_client import http_download


def test_http_download(requests_mock, mocker, tmp_path):
    fake_data = b'fake file contents'

    test_url = 'https://fake-server.com/data/file1.nc'
    filename = os.path.basename(test_url)
    expected_path = tmp_path / filename

    requests_mock.get(test_url, content=fake_data, status_code=200)

    mocker.patch('aviso_client.auth.ensure_credentials',
                 return_value=('user', 'pass'))

    with pytest.raises(FileNotFoundError):
        http_download(test_url, 'bad_path')

    result_path = http_download(test_url, tmp_path)

    assert os.path.exists(result_path)
    assert result_path == str(expected_path)

    with open(result_path, 'rb') as f:
        assert f.read() == fake_data


def test_http_download_error_msg(caplog, tmp_path):
    # TODO Fix this test
    with caplog.at_level(logging.ERROR):
        no_dl = http_download('https://bad_url', tmp_path)

        # assert 'HTTP error : 404 Client Error:  for url: https://bad_url' in caplog.text
        # assert not no_dl
