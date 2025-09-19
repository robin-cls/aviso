import os

from aviso_client.core import details, get, summary


def test_summary():
    catalog = summary()
    assert len(catalog.products) == 2


def test_details():
    details(product_title='Bad Product')
    
    product = details(product_title='Sample Product A')
    assert product.title == 'Sample Product A'
    assert product.id == 'productA'
    assert product.tds_catalog_url == 'https://tds.mock/catalog.xml'
    assert product.abstract == 'This is an abstract.'
    assert product.last_version == '1.2.3'
    assert product.credit == 'Data provided by AVISO'
    assert product.processing_level == 'L2'
    assert product.doi == 'https://doi.org/10.1234/productA'
    assert product.last_update == '2023-06-15'


def test_get(tmp_path):
    local_files = get(product_title='Sample Product A',
                      filter1='A',
                      output_dir=tmp_path,
                      cycle_number=3)

    assert local_files[0] == os.path.join(tmp_path, 'dataset_3.nc')
