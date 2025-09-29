import os
from datetime import datetime

import pytest

from aviso_client.core import details, get, summary


def test_summary():
    catalog = summary()
    assert len(catalog.products) == 2
    assert catalog.products[0].title == 'Sample Product A'
    assert catalog.products[1].title == 'Sample Product B'


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
    assert product.last_update == datetime(2023, 6, 15, 0, 0)


def test_get_error(tmp_path):
    with pytest.raises(ValueError):
        get(product_title='Bad Product', output_dir=tmp_path)


@pytest.mark.parametrize(
    'product_title, filters, files',
    [('Sample Product A', {},
      ['dataset_02.nc', 'dataset_22.nc', 'dataset_03.nc', 'dataset_33.nc']),
     ('Sample Product A', {
         'filter2': 2,
     }, ['dataset_02.nc', 'dataset_22.nc']),
     ('Sample Product A', {
         'a_number': 3
     }, ['dataset_03.nc']),
     ('Sample Product B', {}, ['dataset_04.nc', 'dataset_44.nc']),
     ('Sample Product B', {
         'other_filter': 'bad'
     }, ['dataset_04.nc', 'dataset_44.nc'])])
def test_get(tmp_path, product_title, filters, files):
    local_files = get(product_title=product_title,
                      output_dir=tmp_path,
                      **filters)

    assert local_files == [os.path.join(tmp_path, f) for f in files]


def test_get_bad_product(tmp_path):
    with pytest.raises(ValueError):
        get(product_title='Bad Product', output_dir=tmp_path)


@pytest.mark.parametrize('product_title, filters', [('Sample Product A', {
    'filter2': 'bad',
}), ('Sample Product A', {
    'filter2': 2,
    'a_number': 3
}), ('Sample Product B', {
    'a_number': 55
})])
def test_get_bad_filter(tmp_path, product_title, filters):
    assert get(product_title=product_title, output_dir=tmp_path,
               **filters) == []
