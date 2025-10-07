import logging
import pathlib as pl

import numpy as np

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


def get(product_short_name: str,
        output_dir: str | pl.Path,
        cycle_number: int | list[int] = None,
        pass_number: int | list[int] = None,
        time: tuple[np.datetime64, np.datetime64] = None,
        version: str = None) -> list[str]:
    """Downloads a product from Aviso's Thredds Data Server.

    Parameters
    ----------
    product_short_name
        the short name of the product
    output_dir
        directory to store downloaded product files
    cycle_number
        the cycle number for files/folders selection
    pass_number
        the pass number for files/folders selection
    time
        the period for files/folders selection
    version
        the version for files/folders selection

    Returns
    -------
    list[str]
        the list of downloaded local file paths
    """
    filters = {}
    if not cycle_number is None:
        filters['cycle_number'] = cycle_number
    if not pass_number is None:
        filters['pass_number'] = pass_number
    if not time is None:
        filters['time'] = time
    if not version is None:
        filters['version'] = version

    granule_paths = search_granules(product_short_name, **filters)

    logger.info('%d files to download.', len(granule_paths))
    logger.info('Downloading granules: %s...', list(granule_paths))

    return list(http_bulk_download(list(granule_paths), output_dir))
