import enum
import json
import os
import re

import pytest
from ocean_tools.io import (
    FileNameConvention,
    FileNameFieldInteger,
    FileNameFieldString,
    Layout,
)

import aviso_client
from aviso_client.catalog_parser.granule_discoverer import TDSIterable

############## PATCH GEONETWORK CATALOG RESPONSES


@pytest.fixture
def catalog_response():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'catalog_response.json')
    with open(fixture_path, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def product_response():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'product_response.json')
    with open(fixture_path, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(autouse=True)
def mock_post(mocker, catalog_response):
    mock_post = mocker.patch(
        'aviso_client.catalog_parser.catalog_client.requests.post')
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = catalog_response
    mock_post.return_value = mock_response
    return mock_post


@pytest.fixture(autouse=True)
def mock_get(mocker, product_response):
    mock_get = mocker.patch(
        'aviso_client.catalog_parser.catalog_client.requests.get')
    mock_response = mocker.Mock()
    mock_response.content = b'fake file contents'
    mock_response.status_code = 200
    mock_response.json.return_value = product_response
    mock_get.return_value = mock_response
    return mock_get


############## PATCH GRANULES DISCOVERING


@pytest.fixture
def test_layout():
    return Layout([
        FileNameConvention(re.compile('product(?P<filter1>.*)_path'),
                           [FileNameFieldString('filter1')],
                           'product{filter1!f}_path')
    ])


@pytest.fixture
def test_filename_convention():
    return FileNameConvention(re.compile(r'dataset_(?P<cycle_number>\d{1})'),
                              [FileNameFieldInteger('cycle_number')],
                              'dataset_{cycle_number!f}')


@pytest.fixture
def tds_iterable(test_layout):
    return TDSIterable(test_layout)


@pytest.fixture(autouse=True)
def patch_all(mocker, test_layout, test_filename_convention):

    mocker.patch(
        'aviso_client.catalog_parser.granule_discoverer.TDS_LAYOUT_CONFIG',
        os.path.join(os.path.dirname(__file__), 'fixtures', 'tds_layout.yaml'))

    class FakeAvisoDataType(enum.Enum):
        TEST_TYPE = 'test_type'

        @classmethod
        def from_str(cls, s: str):
            s = s.lower()
            for member in cls:
                if member.value.lower() == s:
                    return member
            raise ValueError(f'Unknown type: {s}')

    mocker.patch(
        'aviso_client.catalog_parser.granule_discoverer.AvisoDataType',
        new=FakeAvisoDataType)
    mocker.patch(
        'aviso_client.catalog_parser.granule_discoverer.PREDEFINED_LAYOUTS', {
            aviso_client.catalog_parser.granule_discoverer.AvisoDataType.TEST_TYPE:
            test_layout
        })
    mocker.patch(
        'aviso_client.catalog_parser.granule_discoverer.PREDEFINED_CONVENTIONS',
        {
            aviso_client.catalog_parser.granule_discoverer.AvisoDataType.TEST_TYPE:
            test_filename_convention
        })

    mocker.patch(
        'aviso_client.catalog_parser.granule_discoverer.TDS_CATALOG_BASE_URL',
        'https://tds.mock/')


############## PATCH TDS CATALOG CONTENT


@pytest.fixture(autouse=True)
def mock_tds_catalog(mocker):
    """Recursive TDSCatalog mock with two sub-catalogs."""

    mock_dataset1 = mocker.Mock()
    mock_dataset1.access_urls = {'HTTPServer': 'https://tds.mock/dataset_1.nc'}

    mock_dataset2 = mocker.Mock()
    mock_dataset2.access_urls = {
        'HTTPServer': 'https://tds.mock/productA_path/dataset_2.nc'
    }
    mock_dataset3 = mocker.Mock()
    mock_dataset3.access_urls = {
        'HTTPServer': 'https://tds.mock/productA_path/dataset_3.nc'
    }

    mock_catalog_vA = mocker.Mock()
    mock_catalog_vA.datasets = {'ds2': mock_dataset2, 'ds3': mock_dataset3}
    mock_catalog_vA.catalog_refs = {}

    mock_ref_vA = mocker.Mock()
    mock_ref_vA.href = 'https://tds.mock/productA_path/catalog.xml'

    mock_dataset4 = mocker.Mock()
    mock_dataset4.access_urls = {
        'HTTPServer': 'https://tds.mock/productB_path/dataset_4.nc'
    }

    mock_catalog_vB = mocker.Mock()
    mock_catalog_vB.datasets = {'ds4': mock_dataset4}
    mock_catalog_vB.catalog_refs = {}

    mock_ref_vB = mocker.Mock()
    mock_ref_vB.href = 'https://tds.mock/productB_path/catalog.xml'

    def tds_catalog_side_effect(url):
        if url == 'https://tds.mock/catalog.xml':
            mock_root = mocker.Mock()
            mock_root.datasets = {'ds1': mock_dataset1}
            mock_root.catalog_refs = {
                'productA_path': mock_ref_vA,
                'productB_path': mock_ref_vB,
            }
            return mock_root
        elif url == 'https://tds.mock/productA_path/catalog.xml':
            return mock_catalog_vA
        elif url == 'https://tds.mock/productB_path/catalog.xml':
            return mock_catalog_vB
        else:
            raise ValueError(f'Unexpected TDSCatalog URL: {url}')

    mocker.patch('aviso_client.catalog_parser.granule_discoverer.TDSCatalog',
                 side_effect=tds_catalog_side_effect)
