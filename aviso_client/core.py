import pathlib as pl

from .catalog_parser.catalog_client import (
    fetch_catalog,
    get_details,
    search_granules,
)
from .catalog_parser.models import AvisoCatalog, AvisoProduct
from .tds_client import http_download


def summary() -> AvisoCatalog:
    """Summarizes CDS-AVISO and SWOT products from AVISO's catalog.

    Returns
    -------
    AvisoCatalog
        the AVISO catalog object containing all the CDS-AVISO and SWOT products
    """
    return fetch_catalog()


def details(product_title: str) -> AvisoProduct:
    """Details a product information from AVISO's catalog.

    Parameters
    ----------
    product_title
        the title of the product

    Returns
    -------
    AvisoProduct
        the product details
    """
    return get_details(product_title)


def get(product_title: str, output_dir: str | pl.Path, **filters) -> list[str]:
    """Downloads a product from AVISO's Thredds Data Server.

    Parameters
    ----------
    product_title
        the title of the product
    output_dir
        directory to store downloaded product files
    **filters
        filters for files selection

    Returns
    -------
    list[str]
        the list of downloaded local file paths
    """
    granule_paths = search_granules(product_title, **filters)
    downloaded = [
        http_download(path, str(output_dir)) for path in granule_paths
    ]
    return [f for f in downloaded if f is not None]
