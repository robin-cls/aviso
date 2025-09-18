import logging
import os

import pytest

from aviso_client.tds_client import http_download


@pytest.fixture
def bad_product_url():
    return 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v500/Basic/cycle_bad/bad_url.nc'


@pytest.fixture
def product_url():
    return 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_495/SWOT_L3_LR_SSH_Basic_495_001_20230418T184522_20230418T193627_v2.0.1.nc'


@pytest.fixture
def product_filename():
    return 'SWOT_L3_LR_SSH_Basic_495_001_20230418T184522_20230418T193627_v2.0.1.nc'


def test_http_download(tmp_path, product_url, product_filename):
    local_file = http_download(product_url, tmp_path)
    assert local_file == os.path.join(tmp_path, product_filename)
    assert os.path.exists(local_file)


def test_http_download_error(product_url):
    with pytest.raises(FileNotFoundError):
        http_download(product_url, 'bad_path')


def test_http_download_error_msg(caplog, tmp_path, bad_product_url):

    with caplog.at_level(logging.ERROR):
        no_dl = http_download(bad_product_url, tmp_path)

        assert 'HTTP error : 404 Client Error:  for url: https://tds-odatis.aviso.altimetry.fr/thredds/fileServer/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v500/Basic/cycle_bad/bad_url.nc' in caplog.text
        assert not no_dl
