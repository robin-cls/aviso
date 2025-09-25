import os

import pytest

from aviso_client.catalog_parser.catalog_client import (
    _get_product_from_title,
    _request_catalog,
    _request_product,
    fetch_catalog,
    get_details,
    search_granules,
)
from aviso_client.catalog_parser.models import AvisoCatalog


def test_request_catalog(mock_post):
    catalog_response = _request_catalog()
    assert catalog_response is not None

    mock_post.assert_called_once()

    expected_url = os.path.join(
        'https://sextant.ifremer.fr/geonetwork/srv/api/',
        'search/records/_search')
    call_args, call_kwargs = mock_post.call_args
    assert call_args[0] == expected_url

    assert 'Accept' in call_kwargs['headers']
    assert call_kwargs['headers']['Accept'] == 'application/json'


def test_request_catalog_http_error(mock_post):
    mock_response = mock_post.MagicMock()
    mock_response.raise_for_status.side_effect = Exception('Server Error 500')
    mock_post.return_value = mock_response
    with pytest.raises(Exception, match='Server Error 500'):
        _request_catalog()


def test_fetch_catalog():
    catalog = fetch_catalog()

    assert isinstance(catalog, AvisoCatalog)
    assert len(catalog.products) == 2
    assert catalog.products[0].title == 'Sample Product A'
    assert catalog.products[1].title == 'Sample Product B'


def test_request_product(mock_get):
    _id = 'id'
    product_response = _request_product(product_id=_id)
    assert product_response is not None

    mock_get.assert_called_once()

    call_args, _ = mock_get.call_args
    assert call_args[
        0] == f'https://sextant.ifremer.fr/geonetwork/srv/api/records/{_id}'


def test_request_product_http_error(mock_get):
    mock_response = mock_get.MagicMock()
    mock_response.raise_for_status.side_effect = Exception('Server Error 500')
    mock_get.return_value = mock_response
    with pytest.raises(Exception, match='Server Error 500'):
        _request_product(product_id='record')


def test_get_details():
    with pytest.raises(ValueError):
        get_details(product_title='Bad Product')

    product = get_details(product_title='Sample Product A')
    assert product.title == 'Sample Product A'
    assert product.id == 'productA'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.abstract == 'This is an abstract.'
    assert product.last_version == '1.2.3'
    assert product.credit == 'Data provided by AVISO'
    assert product.processing_level == 'L2'
    assert product.doi == 'https://doi.org/10.1234/productA'
    assert product.last_update == '2023-06-15'


@pytest.mark.parametrize('title, id', [('Sample Product A', 'productA'),
                                       ('Sample Product A', 'productA')])
def test_get_product_from_title(title, id):
    product = _get_product_from_title(title)

    assert product.id == id
    assert product.title == title

    assert product.tds_catalog_url == f'https://tds.mock/{id}_path/catalog.xml'


def test_get_product_from_title_error():
    with pytest.raises(ValueError):
        _get_product_from_title('Bad Product')


@pytest.mark.parametrize(
    'title, filters, exp_granules',
    [('Sample Product A', {}, [
        'https://tds.mock/productA_path/2_filter/dataset_02.nc',
        'https://tds.mock/productA_path/2_filter/dataset_22.nc',
        'https://tds.mock/productA_path/3_filter/dataset_03.nc',
        'https://tds.mock/productA_path/3_filter/dataset_33.nc'
    ]),
     ('Sample Product A', {
         'filter2': 2,
     }, [
         'https://tds.mock/productA_path/2_filter/dataset_02.nc',
         'https://tds.mock/productA_path/2_filter/dataset_22.nc',
     ]),
     ('Sample Product A', {
         'a_number': 3,
     }, ['https://tds.mock/productA_path/3_filter/dataset_03.nc']),
     ('Sample Product B', {}, [
         'https://tds.mock/productB_path/4_filter/dataset_04.nc',
         'https://tds.mock/productB_path/4_filter/dataset_44.nc'
     ]),
     ('Sample Product B', {
         'other_filter': 'bad'
     }, [
         'https://tds.mock/productB_path/4_filter/dataset_04.nc',
         'https://tds.mock/productB_path/4_filter/dataset_44.nc'
     ])])
def test_search_granules(title, filters, exp_granules):
    granules = search_granules(title, **filters)
    assert list(granules) == exp_granules


def test_search_granules_error():
    with pytest.raises(ValueError):
        search_granules(product_title='Bad Product')


@pytest.mark.parametrize('title, filters', [
    ('Sample Product A', {
        'filter2': 'bad',
    }),
    ('Sample Product A', {
        'filter2': 2,
        'a_number': 3,
    }),
    ('Sample Product B', {
        'a_number': 55
    }),
])
def test_search_granules_bad_filter(title, filters):
    granules = search_granules(title, **filters)
    assert list(granules) == []
