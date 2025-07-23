import os

import yaml
from siphon.catalog import TDSCatalog

from .models import AvisoProduct, Granule

TDS_CATALOGUE_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/catalog/'
TDS_LAYOUT_CONFIG = os.path.join(os.path.dirname(__file__), 'resources',
                                 'tds_layout.yaml')


def filter_granules(product: AvisoProduct, **filters) -> list[Granule]:
    product_layout = _get_product_layout(product)
    granules_path = _fill_granules_path(
        product_layout['granules_path_convention'], **filters)

    # TODO HANDLE CASE time/cycle_number(int or range) filter -> ocean_tools
    # TODO Apply filters using filenames conventions -> ocean_tools
    granules = _fetch_granules(
        os.path.join(TDS_CATALOGUE_BASE_URL, granules_path, 'catalog.xml'))
    granules = _apply_filters(granules, **filters)
    return granules


def _get_product_layout(product: AvisoProduct) -> str:
    # Parse resources/tds_layout.yaml to retrieve the product layout information
    with open(TDS_LAYOUT_CONFIG) as f:
        tds_layout = yaml.safe_load(f)
        return tds_layout[product.id]


def _fill_granules_path(path: str, **filters) -> str:
    # If there is a missing path_filters from filters, raise KeyError
    return path.format(**filters)


def _fetch_granules(tds_catalogue_url: str) -> list[str]:
    # Parse thredds catalogue to fetch granules
    # ex https://tds-odatis.aviso.altimetry.fr/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_004/catalog.xml
    base_catalog = TDSCatalog(tds_catalogue_url)
    return [ds_name for ds_name, _ in base_catalog.datasets.items()]


def _apply_filters(granules: list[str], **filters) -> list[str]:
    return []
