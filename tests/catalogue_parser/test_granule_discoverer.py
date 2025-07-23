import numpy as np

from aviso_client.catalogue_parser import granule_discoverer, models


def test_filter_granules():
    granules = granule_discoverer.filter_granules(
        models.AvisoProduct(id='aa2927ad-d1d6-4867-89d3-1311bc11e6bb'),
        dataset='Basic',
        cycle_number=21,
        pass_number=20)
    g = granules[0]
    assert g.dataset == 'SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc'
    assert g.catalogue == '/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_021/catalog.html'
    assert g.data_size == 3541878
    assert g.file_path == 'dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_021/SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc'
