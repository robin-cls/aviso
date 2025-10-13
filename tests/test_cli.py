import logging

import numpy as np
import pytest
from typer.testing import CliRunner

import aviso_client.core as ac_core
from aviso_client.cli import _setup_logging, app, logger

runner = CliRunner()


def test_setup_logging(mocker):
    handler1 = mocker.Mock()
    handler2 = mocker.Mock()

    mocker.patch.object(logger, 'handlers', [handler1, handler2])

    mock_set_level = mocker.patch.object(logger, 'setLevel')

    _setup_logging(verbose=True)

    mock_set_level.assert_called_once_with(logging.INFO)

    handler1.setLevel.assert_called_once_with(logging.INFO)
    handler2.setLevel.assert_called_once_with(logging.INFO)


def test_main_without_verbose_sets_warning_level():
    logger.setLevel(logging.NOTSET)
    for handler in logger.handlers:
        handler.setLevel(logging.NOTSET)

    result = runner.invoke(app, ['summary'])

    assert result.exit_code == 0
    assert logger.level == logging.WARNING
    for handler in logger.handlers:
        assert handler.level == logging.WARNING


@pytest.fixture
def mock_catalog():
    return ac_core.AvisoCatalog(products=[
        ac_core.AvisoProduct(id='1', short_name='prod1', title='Product 1'),
        ac_core.AvisoProduct(id='2', short_name='prod2', title='Product 2'),
    ])


@pytest.fixture
def mock_product():
    return ac_core.AvisoProduct(
        id='1',
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
        geographic_extent=(-180.0, 180.0, -80.0, 90.0),
        temporal_extent=(np.datetime64('2023-01-01'),
                         np.datetime64('2023-12-31')),
    )


def test_summary(mocker, mock_catalog):
    mocker.patch.object(ac_core, 'summary', return_value=mock_catalog)
    result = runner.invoke(app, ['summary'])
    assert result.exit_code == 0
    assert 'prod1' in result.output
    assert 'prod2' in result.output


def test_details(mocker, mock_product):
    mocker.patch.object(ac_core, 'details', return_value=mock_product)
    result = runner.invoke(app, ['details', 'prod1'])
    assert result.exit_code == 0
    assert 'prod1' in result.output
    assert 'Product: prod1' in result.output
    assert 'keywords' in result.output


def test_details_bad_product(tmp_path):
    result = runner.invoke(app, ['details', 'bad_product'])
    assert result.exit_code != 0
    assert ("Invalid value: 'bad_product' doesn't exist "
            'in Aviso catalog.') in result.output


def test_get_simple_filters(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core,
                                     'get',
                                     return_value=['file_01.nc', 'file_02.nc'])
    result = runner.invoke(
        app,
        [
            'get',
            'AVISO-SWOT',
            '--output',
            str(tmp_path),
            '--version',
            '1.0',
            '--cycle',
            '1',
            '--cycle',
            '2',
        ],
    )
    assert result.exit_code == 0
    assert 'Downloaded files (2)' in result.output
    assert '- file_01.nc' in result.output
    assert '- file_02.nc' in result.output

    mocked_get.assert_called_once_with(
        product_short_name='AVISO-SWOT',
        output_dir=tmp_path,
        version='1.0',
        cycle_number=[1, 2],
        pass_number=None,
        time=(None, None),
    )


def test_get_with_start_only(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core, 'get', return_value=['file.nc'])
    result = runner.invoke(
        app,
        ['get', 'SWOT', '--output',
         str(tmp_path), '--start', '2023-01-01'])
    assert result.exit_code == 0
    args = mocked_get.call_args.kwargs
    assert args['product_short_name'] == 'SWOT'
    assert args['output_dir'] == tmp_path
    assert args['time'] == (
        '2023-01-01',
        None,
    )


def test_get_with_start_and_end(mocker, tmp_path):
    mocked_get = mocker.patch.object(ac_core, 'get', return_value=['file.nc'])
    result = runner.invoke(
        app,
        [
            'get',
            'SWOT',
            '--output',
            str(tmp_path),
            '--start',
            '2023-01-01',
            '--end',
            '2023-01-05',
        ],
    )
    assert result.exit_code == 0
    args = mocked_get.call_args.kwargs
    assert args['time'] == (
        '2023-01-01',
        '2023-01-05',
    )


def test_get_bad_options(tmp_path):
    result = runner.invoke(app, ['get', 'SWOT'])
    assert result.exit_code != 0
    assert "Missing option '--output' / '-o'." in result.output

    result = runner.invoke(app, [
        'get', 'SWOT', '--output',
        str(tmp_path), '--bad_filter', 'bad_value'
    ])
    assert result.exit_code != 0
    assert 'No such option: --bad_filter' in result.output


def test_get_bad_product(tmp_path):
    result = runner.invoke(app,
                           ['get', 'bad_product', '--output',
                            str(tmp_path)])
    assert result.exit_code != 0
    assert ("Invalid value: 'bad_product' doesn't "
            'exist in Aviso catalog.') in result.output
