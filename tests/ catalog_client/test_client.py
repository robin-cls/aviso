import os
from datetime import datetime

import pytest
import requests

from aviso_client.catalog_client.client import (
    _get_product_from_short_name,
    _request_catalog,
    _request_product,
    fetch_catalog,
    get_details,
    InvalidProductError,
    search_granules,
)
from aviso_client.catalog_client.geonetwork.models.dataclasses import AvisoCatalog


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
    assert catalog.products[0].short_name == 'sample_product_a'
    assert catalog.products[1].short_name == 'sample_product_b'


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


def test_request_product_timeout(mocker):
    mocker.patch('requests.get', side_effect=requests.Timeout)

    with pytest.raises(RuntimeError, match='Timeout after .* seconds'):
        _request_product('fake-id', timeout=1.0)


def test_get_details():
    with pytest.raises(InvalidProductError):
        get_details(product_short_name='bad_short_name')

    product = get_details(product_short_name='sample_product_a')
    assert product.title == 'Sample Product A'
    assert product.short_name == 'sample_product_a'
    assert product.id == 'productA'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.abstract == 'This is an abstract.'
    assert product.last_version == '1.2.3'
    assert product.credit == 'Data provided by AVISO'
    assert product.processing_level == 'L2'
    assert product.doi == 'https://doi.org/10.1234/productA'
    assert product.last_update == datetime(2023, 6, 15, 0, 0)


@pytest.mark.parametrize('short_name, id', [('sample_product_a', 'productA'),
                                            ('sample_product_b', 'productB')])
def test_get_product_from_short_name(short_name, id):
    product = _get_product_from_short_name(short_name)

    assert product.id == id
    assert product.short_name == short_name

    assert product.tds_catalog_url == f'https://tds.mock/{id}_path/catalog.xml'


def test_get_product_from_short_name_error():
    with pytest.raises(InvalidProductError):
        _get_product_from_short_name('bad_short_name')


@pytest.mark.parametrize(
    'short_name, filters, exp_granules',
    [('sample_product_a', {}, [
        'https://tds.mock/productA_path/2_filter/dataset_02.nc',
        'https://tds.mock/productA_path/2_filter/dataset_22.nc',
        'https://tds.mock/productA_path/3_filter/dataset_03.nc',
        'https://tds.mock/productA_path/3_filter/dataset_33.nc'
    ]),
     ('sample_product_a', {
         'filter2': 2,
     }, [
         'https://tds.mock/productA_path/2_filter/dataset_02.nc',
         'https://tds.mock/productA_path/2_filter/dataset_22.nc',
     ]),
     ('sample_product_a', {
         'a_number': 3,
     }, ['https://tds.mock/productA_path/3_filter/dataset_03.nc']),
     ('sample_product_b', {}, [
         'https://tds.mock/productB_path/4_filter/dataset_04.nc',
         'https://tds.mock/productB_path/4_filter/dataset_44.nc'
     ]),
     ('sample_product_b', {
         'other_filter': 'bad'
     }, [
         'https://tds.mock/productB_path/4_filter/dataset_04.nc',
         'https://tds.mock/productB_path/4_filter/dataset_44.nc'
     ])])
def test_search_granules(short_name, filters, exp_granules):
    granules = search_granules(short_name, **filters)
    assert list(granules) == exp_granules


def test_search_granules_error():
    with pytest.raises(InvalidProductError):
        search_granules(product_short_name='Bad Product')


@pytest.mark.parametrize('short_name, filters', [
    ('sample_product_a', {
        'filter2': 'bad',
    }),
    ('sample_product_a', {
        'filter2': 2,
        'a_number': 3,
    }),
    ('sample_product_b', {
        'a_number': 55
    }),
])
def test_search_granules_bad_filter(short_name, filters):
    granules = search_granules(short_name, **filters)
    assert list(granules) == []
