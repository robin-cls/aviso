import os

from aviso_client.tds_client import http_download

def test_http_download(tmp_path):
    local_file = http_download(
        'dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_021/SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc',
        tmp_path)
    assert local_file == os.path.join(
        tmp_path,
        'SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc'
    )
    assert os.path.exists(local_file)
