import logging
from datetime import datetime

import numpy as np
import pytest

from aviso_client.catalog_client.geonetwork.models.model import (
    AvisoCatalog,
    AvisoProduct,
)
from aviso_client.catalog_client.geonetwork.response_parser import (
    parse_catalog_response,
    parse_product_response,
)


def test_parse_catalog_response(catalog_response):
    catalog = parse_catalog_response(catalog_response)
    assert isinstance(catalog, AvisoCatalog)
    assert len(catalog.products) == 2

    p1 = catalog.products[0]
    assert p1.id == 'productA'
    assert p1.title == 'Sample Product A'
    assert p1.keywords == 'keywordA, keywordAA'
    assert p1.tds_catalog_url == 'https://tds.mock/productA_path/catalog.xml'
    assert p1.short_name == 'sample_product_a'
    assert p1.doi == 'https://doi.org/10.1234/productA'
    assert p1.last_update == datetime(2023, 6, 15, 0, 0)

    p2 = catalog.products[1]
    assert p2.id == 'productB'
    assert p2.title == 'Sample Product B'
    assert p2.keywords == 'keywordB'
    assert p2.short_name == 'sample_product_b'
    assert p2.last_update == datetime(2022, 5, 20, 0, 0)


def test_parse_catalog_response2(catalog_response2):
    catalog = parse_catalog_response(catalog_response2)
    assert isinstance(catalog, AvisoCatalog)
    assert len(catalog.products) == 2

    p1 = catalog.products[0]
    assert p1.id == 'productA'
    assert p1.title == 'Sample Product A'
    assert p1.keywords == 'keywordA, keywordAA'
    assert p1.doi == 'https://doi.org/10.1234/productA'
    assert p1.last_update == datetime(2023, 6, 15, 0, 0)

    p2 = catalog.products[1]
    assert p2.id == 'productB'
    assert p2.title == 'Sample Product B'
    assert p2.keywords == 'keywordB'
    assert p2.last_update == datetime(2022, 5, 20, 0, 0)


def test_parse_bad_catalog_response(bad_catalog_response, caplog):
    with pytest.raises(RuntimeError):
        parse_catalog_response(bad_catalog_response)

    assert ('A validation error happened when '
            "parsing Aviso's catalog response") in caplog.text
    assert 'hits.hits' in caplog.text
    assert 'Input should be a valid list' in caplog.text


def test_parse_product_response(product_response):
    product = parse_product_response(product_response,
                                     AvisoProduct(id='productA'))

    assert product.id == 'productA'
    assert product.last_version == '1.2.3'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.processing_level == 'L2'
    assert product.abstract == 'This is an abstract.'
    assert product.credit == 'Data provided by AVISO'
    assert product.geographic_extent == (-180.0, 180.0, -80.0, 80.0)
    assert product.temporal_extent == (np.datetime64('2023-03-29'), None)


def test_parse_product_response2(product_response2):
    product = parse_product_response(product_response2,
                                     AvisoProduct(id='productA'))

    assert product.id == 'productA'
    assert product.tds_catalog_url == ''
    assert product.processing_level == 'L2'
    assert product.abstract == 'This is an abstract.'
    assert product.credit == 'Data provided by AVISO'
    assert product.geographic_extent == (15.0, 50.0, -40.0, 0)
    assert product.temporal_extent == (np.datetime64('2023-03-29'),
                                       np.datetime64('2024-03-29'))


def test_parse_bad_product_responses(bad_product_responses, caplog):
    for bad_product_response in bad_product_responses:
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            parse_product_response(bad_product_response,
                                   AvisoProduct(id='productA'))

        assert ("A validation error happened when parsing Aviso's "
                'catalog response for product: productA.') in caplog.text
