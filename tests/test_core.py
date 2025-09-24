import os

import pytest

from aviso_client.core import details, get, summary


def test_summary():
    catalog = summary()
    assert len(catalog.products) == 2


def test_details():
    with pytest.raises(ValueError):
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


def test_get_error(tmp_path):
    with pytest.raises(ValueError):
        get(product_title='Bad Product', output_dir=tmp_path)


@pytest.mark.parametrize('product_title, filters, files', [
    ('Sample Product A', {},
     ['dataset_02.nc', 'dataset_22.nc', 'dataset_03.nc', 'dataset_33.nc']),
    ('Sample Product A', {
        'filter1': 'A',
        'a_number': 3
    }, ['dataset_03.nc']),
    ('Sample Product B', {
        'filter1': 'A',
        'a_number': 3
    }, []),
    ('Sample Product B', {}, ['dataset_04.nc', 'dataset_44.nc']),
])
def test_get(tmp_path, product_title, filters, files):
    local_files = get(product_title=product_title,
                      output_dir=tmp_path,
                      **filters)

    assert local_files == [os.path.join(tmp_path, f) for f in files]
