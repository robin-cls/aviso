import pytest
import os
import json
from unittest.mock import MagicMock

@pytest.fixture
def catalog_response():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'catalog_response.json')
    with open(fixture_path, encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def product_response():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'product_response.json')
    with open(fixture_path, encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(autouse=True)
def mock_tds_catalog(mocker):
    """Recursive TDSCatalog mock with two sub-catalogs."""

    mock_dataset1 = MagicMock()
    mock_dataset1.access_urls = {'HTTPServer': 'https://tds.mock/dataset1.nc'}

    mock_dataset2 = MagicMock()
    mock_dataset2.access_urls = {'HTTPServer': 'https://tds.mock/vA/dataset2.nc'}

    mock_catalog_vA = MagicMock()
    mock_catalog_vA.datasets = {'ds2': mock_dataset2}
    mock_catalog_vA.catalog_refs = {}

    mock_ref_vA = MagicMock()
    mock_ref_vA.href = 'https://tds.mock/A/catalog.xml'

    mock_dataset3 = MagicMock()
    mock_dataset3.access_urls = {'HTTPServer': 'https://tds.mock/vB/dataset3.nc'}

    mock_catalog_vB = MagicMock()
    mock_catalog_vB.datasets = {'ds3': mock_dataset3}
    mock_catalog_vB.catalog_refs = {}

    mock_ref_vB = MagicMock()
    mock_ref_vB.href = 'https://tds.mock/B/catalog.xml'

    def tds_catalog_side_effect(url):
        if url == 'https://tds.mock/catalog.xml':
            mock_root = MagicMock()
            mock_root.datasets = {'ds1': mock_dataset1}
            mock_root.catalog_refs = {
                'A': mock_ref_vA,
                'B': mock_ref_vB,
            }
            return mock_root
        elif url == 'https://tds.mock/A/catalog.xml':
            return mock_catalog_vA
        elif url == 'https://tds.mock/B/catalog.xml':
            return mock_catalog_vB
        else:
            raise ValueError(f"Unexpected TDSCatalog URL: {url}")

    mocker.patch('aviso_client.catalog_parser.granule_discoverer.TDSCatalog', side_effect=tds_catalog_side_effect)