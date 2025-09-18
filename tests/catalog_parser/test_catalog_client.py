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


@pytest.fixture(autouse=True)
def mock_post(mocker, catalog_response):
    mock_post = mocker.patch(
        'aviso_client.catalog_parser.catalog_client.requests.post')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = catalog_response
    mock_post.return_value = mock_response
    return mock_post


@pytest.fixture(autouse=True)
def mock_get(mocker, product_response):
    mock_get = mocker.patch(
        'aviso_client.catalog_parser.catalog_client.requests.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = product_response
    mock_get.return_value = mock_response
    return mock_get


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
    # TODO
    # product = get_details(product_title='Sample SWOT Product 1')
    pass


@pytest.mark.parametrize('title, id', [('Sample Product 1', 'product1'),
                                       ('Sample Product 2', 'product2')])
def test_get_product_from_title(title, id):
    product = _get_product_from_title(title)

    assert product.id == id
    assert product.title == title

    assert product.tds_catalog_url == f'https://tds.mock/{id}/catalog.xml'


def test_search_granules():
    return
