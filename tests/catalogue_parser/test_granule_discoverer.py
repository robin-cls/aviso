import pytest

from aviso_client.catalog_parser.granule_discoverer import filter_granules
from aviso_client.catalog_parser.models import AvisoProduct


@pytest.fixture
def swot_l3_product():
    return AvisoProduct(id='aa2927ad-d1d6-4867-89d3-1311bc11e6bb')


@pytest.mark.parametrize('filters', [{
    'subset': 'Basic'
}, {
    'version': 'v2_0_1'
}])
def test_filter_granules_keyerror(swot_l3_product, filters):
    with pytest.raises(KeyError):
        filter_granules(swot_l3_product, **filters)


@pytest.mark.parametrize('filters', [
    {
        'subset': 'bad'
    },
    {
        'version': 'bad'
    },
])
def test_filter_granules_valueerror(swot_l3_product, filters):
    with pytest.raises(ValueError):
        filter_granules(swot_l3_product, **filters)


@pytest.mark.parametrize('subset, cycle_number, pass_number', [
    ('Basic', 21, 20),
])
def test_filter_granules(swot_l3_product, subset, cycle_number, pass_number):
    filters = {
        'subset': subset,
        'cycle_number': cycle_number,
        'pass_number': pass_number
    }
    granules = filter_granules(swot_l3_product, **filters)

    g = granules[0]
    assert g == 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_021/SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc'
