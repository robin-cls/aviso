from .models import Granule


def fetch_granules(tds_catalogue_url: str) -> list[Granule]:
    # interrogates thredds catalogue to fetch granules
    # time consuming to fetch https://tds-odatis.aviso.altimetry.fr/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v2_0_1/Basic/catalog.xml
    return []


def filter_granules(tds_catalogue_url: str, **filters) -> list[Granule]:
    return []
