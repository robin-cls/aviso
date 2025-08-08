from aviso_client.catalog_parser.catalog_client import fetch_catalog, get_details, search_granules


def test_fetch_catalog():
    catalog = fetch_catalog()
    assert len(catalog.products) == 12


def test_get_details():
    product = get_details(
        'Wind & Wave product SWOT Level-3 WindWave - Light')
    assert product.title == 'Wind & Wave product SWOT Level-3 WindWave - Light'
    assert product.id == '15f25d0b-5a41-4335-85f2-874e9b2e5cd0'
    assert product.tds_catalog_url == 'https://tds%40odatis-ocean.fr:odatis@tds-odatis.aviso.altimetry.fr/thredds/catalog/L3/SWOT_KARIN-L3_LR_WIND_WAVE.html'

    product = get_details(
        'Altimetry product SWOT Level-3 Low Rate SSH - Basic')
    assert product.title == 'Altimetry product SWOT Level-3 Low Rate SSH - Basic'
    assert product.id == 'aa2927ad-d1d6-4867-89d3-1311bc11e6bb'
    assert product.tds_catalog_url == 'https://tds%40odatis-ocean.fr:odatis@tds-odatis.aviso.altimetry.fr/thredds/catalog/L3/SWOT_KARIN-L3_LR_SSH.html'

    product = get_details(
        'Altimetry product SWOT Level-2 KaRIn Low Rate SSH - Basic')
    assert product.title == 'Altimetry product SWOT Level-2 KaRIn Low Rate SSH - Basic'
    assert product.id == '2652e825-9ade-435c-afdd-eb920d01b018'
    assert product.tds_catalog_url == 'https://tds.aviso.altimetry.fr/thredds/L2/L2-SWOT-DATA/L2-SWOT.html'


def test_search_granules():
    granules = search_granules(
        'Altimetry product SWOT Level-3 Low Rate SSH - Basic',
        subset='Basic',
        cycle_number=21,
        pass_number=20)
    g = granules[0]
    assert g == 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_021/SWOT_L3_LR_SSH_Basic_021_020_20240911T045252_20240911T054418_v2.0.1.nc'
