import os

from siphon.catalog import TDSCatalog

from .models import AvisoProduct, Granule

TDS_CATALOGUE_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/catalog/'


def filter_granules(product: AvisoProduct, **filters) -> list[Granule]:
    granules_path = _get_granules_path(product.id, **filters)
    # TODO HANDLE CASE no cycle but time filter
    granules = _fetch_granules(
        os.path.join(TDS_CATALOGUE_BASE_URL, granules_path, 'catalog.xml'))
    granules = _apply_filters(granules, **filters)
    return granules


def _get_granules_path(id: str, **filters) -> str:
    # Parse resources/tds_layout.yaml to retrieve the path where to find granules
    # if no cycle filter, check that a time filter is present
    # if version/dataset are missing from filters, raise an error
    return ''


def _fetch_granules(tds_catalogue_url: str) -> list[str]:
    # Parse thredds catalogue to fetch granules
    # ex https://tds-odatis.aviso.altimetry.fr/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/cycle_004/catalog.xml
    base_catalog = TDSCatalog(tds_catalogue_url)
    return [ds_name for ds_name, _ in base_catalog.datasets.items()]


def _apply_filters(granules: list[str], **filters) -> list[str]:
    # apply filters using filenames conventions -> ocean_tools
    return []
