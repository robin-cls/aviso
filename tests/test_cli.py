import numpy as np
import pytest
from typer.testing import CliRunner

import aviso_client.core as ac_core
from aviso_client.cli import app

runner = CliRunner()


@pytest.fixture
def mock_catalog():
    return ac_core.AvisoCatalog(products=[
        ac_core.AvisoProduct(id='1', short_name='prod1', title='Product 1'),
        ac_core.AvisoProduct(id='2', short_name='prod2', title='Product 2'),
    ])


@pytest.fixture
def mock_product():
    return ac_core.AvisoProduct(id='1',
                                short_name='prod1',
                                title='Product 1',
                                keywords='sea,altimetry',
                                abstract='Product description',
                                processing_level='L2',
                                tds_catalog_url='http://example.com/thredds',
                                doi='10.1234/aviso.prod1',
                                last_update='2023-10-01',
                                last_version='v1.0',
                                credit='CNES',
                                contact='aviso@altimetry.fr',
                                resolution='0.25',
                                geographical_extent=(-180.0, 180.0, -80.0,
                                                     90.0),
                                temporal_extent=(np.datetime64('2023-01-01'),
                                                 np.datetime64('2023-12-31')))


def test_summary(mocker, mock_catalog):
    mocker.patch.object(ac_core, 'summary', return_value=mock_catalog)
    result = runner.invoke(app, ['summary'])
    assert result.exit_code == 0
    assert 'prod1' in result.output
    assert 'prod2' in result.output


def test_details(mocker, mock_product):
    mocker.patch.object(ac_core, 'details', return_value=mock_product)
    result = runner.invoke(app, ['details', '--product', 'prod1'])
    assert result.exit_code == 0
    assert 'prod1' in result.output
    assert "Product's details: prod1" in result.output
    assert 'keywords' in result.output


def test_get_simple_filters(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core,
                                     'get',
                                     return_value=['file1.nc', 'file2.nc'])
    result = runner.invoke(app, [
        'get',
        '--product',
        'AVISO-SWOT',
        '--output',
        str(tmp_path),
        '--filter',
        'version=1',
        '--filter',
        'resolution=0.25',
    ])
    assert result.exit_code == 0
    assert 'Downloaded files (2)' in result.output
    assert '- file1.nc' in result.output
    assert '- file2.nc' in result.output

    mocked_get.assert_called_once_with(product_short_name='AVISO-SWOT',
                                       output_dir=tmp_path,
                                       version=1,
                                       resolution=0.25)


def test_get_with_start_only(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core, 'get', return_value=['file.nc'])
    result = runner.invoke(app, [
        'get', '--product', 'SWOT', '--output',
        str(tmp_path), '--filter', 'start=2023-01-01'
    ])
    assert result.exit_code == 0
    args = mocked_get.call_args.kwargs
    assert args['product_short_name'] == 'SWOT'
    assert args['output_dir'] == tmp_path
    assert args['time'] == (
        np.datetime64('2023-01-01'),
        np.datetime64('2023-01-01'),
    )


def test_get_with_start_and_end(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core, 'get', return_value=['file.nc'])
    result = runner.invoke(app, [
        'get', '--product', 'SWOT', '--output',
        str(tmp_path), '--filter', 'start=2023-01-01', '--filter',
        'end=2023-01-05'
    ])
    assert result.exit_code == 0
    args = mocked_get.call_args.kwargs
    assert args['time'] == (
        np.datetime64('2023-01-01'),
        np.datetime64('2023-01-05'),
    )


def test_get_invalid_filter_format(tmp_path):
    result = runner.invoke(app, [
        'get', '--product', 'SWOT', '--output',
        str(tmp_path), '--filter', 'not_a_key_value'
    ])
    assert result.exit_code != 0
    assert 'filter is not key=value' in result.output
