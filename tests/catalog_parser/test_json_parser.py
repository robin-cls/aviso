from aviso_client.catalog_parser.json_parser import (
    parse_catalog_response,
    parse_product_response,
)
from aviso_client.catalog_parser.models import AvisoCatalog, AvisoProduct


def test_parse_catalog_response(catalog_response):
    catalog = parse_catalog_response(catalog_response)
    assert isinstance(catalog, AvisoCatalog)
    assert len(catalog.products) == 2

    p1 = catalog.products[0]
    assert p1.id == 'product1'
    assert p1.title == 'Sample Product 1'
    assert p1.keywords == ['keyword1', 'keyword2']
    assert p1.tds_catalog_url == 'https://tds.mock/product1/catalog.xml'
    assert p1.short_name == 'prod1_short'
    assert p1.doi == 'https://doi.org/10.1234/product1'
    assert p1.last_update == '2023-06-15'

    p2 = catalog.products[1]
    assert p2.id == 'product2'
    assert p2.title == 'Sample Product 2'
    assert p2.keywords == ['keywordA']
    assert p2.last_update == '2022-05-20'


def test_parse_product_response(product_response):
    product = parse_product_response(product_response, AvisoProduct(id='id'))

    assert product.id == 'id'
    assert product.last_version == '1.2.3'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.processing_level == 'L2'
    assert product.abstract == 'This is an abstract.'
    assert product.credit == 'Data provided by AVISO'
