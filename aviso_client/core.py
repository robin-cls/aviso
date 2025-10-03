import logging
import pathlib as pl

from .catalog_client.client import (
    fetch_catalog,
    get_details,
    search_granules,
)
from .catalog_client.geonetwork.models.dataclasses import AvisoCatalog, AvisoProduct
from .tds_client import http_bulk_download

logger = logging.getLogger(__name__)


def summary() -> AvisoCatalog:
    """Summarizes CDS-AVISO and SWOT products from AVISO's catalog.

    Returns
    -------
    AvisoCatalog
        the AVISO catalog object containing all the CDS-AVISO and SWOT products
    """
    return fetch_catalog()


def details(product_short_name: str) -> AvisoProduct:
    """Details a product information from AVISO's catalog.

    Parameters
    ----------
    product_short_name
        the short name of the product

    Returns
    -------
    AvisoProduct
        the product details
    """
    return get_details(product_short_name)


def get(product_short_name: str, output_dir: str | pl.Path,
        **filters) -> list[str]:
    """Downloads a product from AVISO's Thredds Data Server.

    Parameters
    ----------
    product_short_name
        the short name of the product
    output_dir
        directory to store downloaded product files
    **filters
        filters for files/folders selection

    Returns
    -------
    list[str]
        the list of downloaded local file paths
    """
    granule_paths = search_granules(product_short_name, **filters)

    logger.info('%d files to download.', len(granule_paths))
    logger.info('Downloading granules: %s...', list(granule_paths))

    return list(http_bulk_download(list(granule_paths), output_dir))
