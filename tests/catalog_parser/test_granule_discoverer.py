import pytest
from requests.exceptions import ProxyError

import aviso_client
from aviso_client.catalog_parser.granule_discoverer import (
    _load_convention_layout,
    _parse_tds_layout,
    filter_granules,
)
from aviso_client.catalog_parser.models.dataclasses import (
    AvisoProduct,
    ProductLayoutConfig,
)


class Test_TDSIterable:

    @pytest.mark.parametrize(
        'filter, exp_urls',
        [({}, [
            'https://tds.mock/dataset_01.nc',
            'https://tds.mock/productA_path/2_filter/dataset_02.nc',
            'https://tds.mock/productA_path/2_filter/dataset_22.nc',
            'https://tds.mock/productA_path/3_filter/dataset_03.nc',
            'https://tds.mock/productA_path/3_filter/dataset_33.nc',
            'https://tds.mock/productB_path/4_filter/dataset_04.nc',
            'https://tds.mock/productB_path/4_filter/dataset_44.nc'
        ]),
         ({
             'filter2': [3, 4]
         }, [
             'https://tds.mock/dataset_01.nc',
             'https://tds.mock/productA_path/3_filter/dataset_03.nc',
             'https://tds.mock/productA_path/3_filter/dataset_33.nc',
             'https://tds.mock/productB_path/4_filter/dataset_04.nc',
             'https://tds.mock/productB_path/4_filter/dataset_44.nc',
         ]),
         ({
             'filter1': 'A'
         }, [
             'https://tds.mock/dataset_01.nc',
             'https://tds.mock/productA_path/2_filter/dataset_02.nc',
             'https://tds.mock/productA_path/2_filter/dataset_22.nc',
             'https://tds.mock/productA_path/3_filter/dataset_03.nc',
             'https://tds.mock/productA_path/3_filter/dataset_33.nc'
         ]),
         ({
             'filter1': 'A',
             'filter2': 3
         }, [
             'https://tds.mock/dataset_01.nc',
             'https://tds.mock/productA_path/3_filter/dataset_03.nc',
             'https://tds.mock/productA_path/3_filter/dataset_33.nc'
         ]),
         ({
             'filter1': 'B'
         }, [
             'https://tds.mock/dataset_01.nc',
             'https://tds.mock/productB_path/4_filter/dataset_04.nc',
             'https://tds.mock/productB_path/4_filter/dataset_44.nc'
         ]), ({
             'filter1': 'C'
         }, [
             'https://tds.mock/dataset_01.nc',
         ]), ({
             'filter2': '6'
         }, [
             'https://tds.mock/dataset_01.nc',
         ])])
    def test_find(self, tds_iterable, filter, exp_urls):
        urls = tds_iterable.find('https://tds.mock/catalog.xml', **filter)

        assert urls == exp_urls

    @pytest.mark.parametrize('filter, exp_urls', [({
        'bad_filter': 'B'
    }, [
        'https://tds.mock/dataset_01.nc',
        'https://tds.mock/productA_path/2_filter/dataset_02.nc',
        'https://tds.mock/productA_path/2_filter/dataset_22.nc',
        'https://tds.mock/productA_path/3_filter/dataset_03.nc',
        'https://tds.mock/productA_path/3_filter/dataset_33.nc',
        'https://tds.mock/productB_path/4_filter/dataset_04.nc',
        'https://tds.mock/productB_path/4_filter/dataset_44.nc'
    ])])
    def test_find_bad_filter(self, tds_iterable, filter, exp_urls):
        with pytest.warns(
                UserWarning,
                match=
                'Layout has been configured with unknown references \'{\'bad_filter\'}\'. They will be ignored.'
        ):
            urls = tds_iterable.find('https://tds.mock/catalog.xml', **filter)
            assert urls == exp_urls

    def test_find_bad_url(self, tds_iterable):
        with pytest.raises(ProxyError) as exc_info:
            tds_iterable.find('https://bad_url/catalog.xml')

        assert "HTTPSConnectionPool(host='https://bad_url/catalog.xml', port=443): Max retries exceeded with url: /L2-SWOT.html (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 503 Service Unavailable'))" in str(
            exc_info.value)


def test_filter_granules():
    urls = filter_granules(AvisoProduct(id='productA'))
    assert list(urls) == [
        'https://tds.mock/productA_path/2_filter/dataset_02.nc',
        'https://tds.mock/productA_path/2_filter/dataset_22.nc',
        'https://tds.mock/productA_path/3_filter/dataset_03.nc',
        'https://tds.mock/productA_path/3_filter/dataset_33.nc',
    ]
    urls = filter_granules(AvisoProduct(id='productA'), a_number=3)
    assert list(urls) == [
        'https://tds.mock/productA_path/3_filter/dataset_03.nc'
    ]


def test_load_convention_layout(patch_some, test_layout,
                                test_filename_convention):
    conf = {
        'TEST_TYPE': ['FileNameConventionSwotL3', 'AVISO_L3_LR_SSH_LAYOUT']
    }

    conv, layout = _load_convention_layout(conf, 'TEST_TYPE')
    assert type(conv) == type(test_filename_convention)
    assert layout == test_layout


@pytest.mark.parametrize('_id, title, filter1',
                         [('productA', 'Sample Product A', 'A'),
                          ('productB', 'Sample Product B', 'B')])
def test_parse_tds_layout(patch_some, test_layout, test_filename_convention,
                          _id, title, filter1):
    pl_conf = _parse_tds_layout(AvisoProduct(id=_id))
    assert isinstance(pl_conf, ProductLayoutConfig)

    assert pl_conf.id == _id
    assert pl_conf.default_filters == {'filter1': filter1}
    assert pl_conf.catalog_path == f'{_id}_path'
    assert pl_conf.title == title
    assert pl_conf.layout == test_layout
    assert type(pl_conf.convention) == type(test_filename_convention)
