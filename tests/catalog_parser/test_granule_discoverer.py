import pytest

import aviso_client
from aviso_client.catalog_parser.granule_discoverer import (
    _parse_tds_layout,
    ConventionLoader,
    filter_granules,
)
from aviso_client.catalog_parser.models import (
    AvisoProduct,
    ProductLayoutConfig,
)


class Test_ConventionLoader:

    def testload(self, test_layout_product, test_filename_convention):
        convention, layout = ConventionLoader().load(
            aviso_client.catalog_parser.granule_discoverer.AvisoDataType.
            TEST_TYPE)

        assert layout == test_layout_product
        assert convention == test_filename_convention


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
         ]),
         ({
             'filter1': 'B',
             'filter2': 6
         }, ['https://tds.mock/dataset_01.nc'])])
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


@pytest.mark.parametrize('_id, title, filter1',
                         [('productA', 'Sample Product A', 'A'),
                          ('productB', 'Sample Product B', 'B')])
def test_parse_tds_layout(test_layout_product, test_filename_convention, _id,
                          title, filter1):
    pl_conf = _parse_tds_layout(AvisoProduct(id=_id))
    assert isinstance(pl_conf, ProductLayoutConfig)

    assert pl_conf.id == _id
    assert pl_conf.default_filters == {'filter1': filter1}
    assert pl_conf.catalog_path == f'{_id}_path'
    assert pl_conf.title == title
    assert pl_conf.layout == test_layout_product
    assert pl_conf.convention == test_filename_convention
