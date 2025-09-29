from datetime import datetime

from aviso_client.catalog_parser.catalog_response_parser import (
    parse_catalog_response,
    parse_product_response,
)
from aviso_client.catalog_parser.models.dataclasses import AvisoCatalog, AvisoProduct


def test_parse_catalog_response(catalog_response):
    catalog = parse_catalog_response(catalog_response)
    assert isinstance(catalog, AvisoCatalog)
    assert len(catalog.products) == 2

    p1 = catalog.products[0]
    assert p1.id == 'productA'
    assert p1.title == 'Sample Product A'
    assert p1.keywords == 'keywordA, keywordAA'
    assert p1.tds_catalog_url == 'https://tds.mock/productA_path/catalog.xml'
    assert p1.short_name == 'prodA_short'
    assert p1.doi == 'https://doi.org/10.1234/productA'
    assert p1.last_update == datetime(2023, 6, 15, 0, 0)

    p2 = catalog.products[1]
    assert p2.id == 'productB'
    assert p2.title == 'Sample Product B'
    assert p2.keywords == 'keywordB'
    assert p2.last_update == datetime(2022, 5, 20, 0, 0)


def test_parse_product_response(product_response):
    product = parse_product_response(product_response,
                                     AvisoProduct(id='productA'))

    assert product.id == 'productA'
    assert product.last_version == '1.2.3'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.processing_level == 'L2'
    assert product.abstract == 'This is an abstract.'
    assert product.credit == 'Data provided by AVISO'
