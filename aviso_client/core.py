from catalogue_parser.catalogue_client import (fetch_catalogue, get_details,
                                               search_granules)
from catalogue_parser.models import AvisoCatalogue, AvisoProduct
from tds_client import http_download


def summary() -> AvisoCatalogue:
    return fetch_catalogue()


def details(product_name: str) -> AvisoProduct:
    return get_details(product_name)


def get(product_name: str, output_dir: str, **filters) -> list[str]:
    granules = search_granules(product_name, **filters)
    return [http_download(g.file_path, output_dir) for g in granules]
