import os

import requests

from .geonetwork.query_builder import GeoNetworkQueryBuilder
from .geonetwork.models.dataclasses import AvisoCatalog, AvisoProduct
from .geonetwork.response_parser import parse_catalog_response, parse_product_response
from .granule_discoverer import filter_granules

AVISO_CATALOG_URL = 'https://sextant.ifremer.fr/geonetwork/srv/api'


def fetch_catalog() -> AvisoCatalog:
    """Fetches CDS-AVISO and SWOT products from AVISO's catalog.

    Returns
    -------
    AvisoCatalog
        the AVISO catalog object containing all the CDS-AVISO and SWOT products
    """
    resp = _request_catalog()
    catalog = parse_catalog_response(resp)
    return catalog


def get_details(product_short_name: str) -> AvisoProduct:
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
    product = _get_product_from_short_name(product_short_name)
    resp = _request_product(product.id)
    product = parse_product_response(resp, product)
    return product


def search_granules(product_short_name: str, **filters) -> list[str]:
    """Search for granules of a product in AVISO's Thredds Data Server.

    Parameters
    ----------
    product_short_name
        the short name of the product
    **filters
        filters for files selection

    Returns
    -------
    list[str]
        the urls of the granules corresponding to the provided filters
    """
    product = _get_product_from_short_name(product_short_name)
    return filter_granules(product, **filters)


def _get_product_from_short_name(product_short_name: str) -> AvisoProduct:
    """Search for a product in AVISO's catalog from its short name."""
    catalog = fetch_catalog()
    for p in catalog.products:
        if p.short_name == product_short_name:
            return p
    raise ValueError(f'Invalid product short_name "{product_short_name}"')


def _request_catalog() -> dict:
    """Request AVISO's catalog products: filters on CDS-AVISO and SWOT."""
    url = os.path.join(AVISO_CATALOG_URL, 'search/records/_search')
    
    builder = GeoNetworkQueryBuilder()
    payload = (
        builder
        .must_match("th_odatis_centre_donnees.default", "CDS-AVISO")
        .must_match("platforms", "SWOT")
        .must_not_term("_id", "94cd8b08-bf24-4f59-8ce5-bc27c6bd9c17")
        .must_not_term("_id", "a57da16f-330a-4927-b532-ca013b6c83da")
        .build()
    )

    resp = requests.post(url,
                         json=payload,
                         headers={'Accept': 'application/json'})
    resp.raise_for_status()

    return resp.json()


def _request_product(product_id: str, timeout: float = 10.0):
    """Request AVISO's catalog product details."""
    url = os.path.join(AVISO_CATALOG_URL, 'records', product_id)

    try:
        resp = requests.get(url,
                            headers={'Accept': 'application/json'},
                            timeout=timeout)
        resp.raise_for_status()

    except requests.Timeout:
        raise RuntimeError(
            f'Timeout after {timeout} seconds when requesting {url}')

    except requests.RequestException as e:
        raise RuntimeError(f'HTTP Error : {e}')

    return resp.json()
