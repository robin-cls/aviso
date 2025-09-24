import os

import requests

from .granule_discoverer import filter_granules
from .json_parser import parse_catalog_response, parse_product_response
from .models import AvisoCatalog, AvisoProduct

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


def get_details(product_title: str) -> AvisoProduct:
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
    product = _get_product_from_title(product_title)
    resp = _request_product(product.id)
    product = parse_product_response(resp, product)
    return product


def search_granules(product_title: str, **filters) -> list[str]:
    """Search for granules of a product in AVISO's Thredds Data Server.

    Parameters
    ----------
    product_title
        the title of the product
    **filters
        filters for files selection

    Returns
    -------
    list[str]
        the urls of the granules corresponding to the provided filters
    """
    product = _get_product_from_title(product_title)
    return filter_granules(product, **filters)


def _get_product_from_title(product_title: str) -> AvisoProduct:
    """Search for a product in AVISO's catalog from its title."""
    catalog = fetch_catalog()
    for p in catalog.products:
        if p.title == product_title:
            return p
    raise ValueError(f'Invalid product title "{product_title}"')


def _request_catalog() -> dict:
    """Request AVISO's catalog products: filters on CDS-AVISO and SWOT."""
    url = os.path.join(AVISO_CATALOG_URL, 'search/records/_search')
    payload = {
        'from': 0,
        'size': 20,
        'query': {
            'bool': {
                'must': [{
                    'match': {
                        'th_odatis_centre_donnees.default': 'CDS-AVISO'
                    }
                }, {
                    'match': {
                        'platforms': 'SWOT'
                    }
                }],
                'must_not': [{
                    'term': {
                        '_id': '94cd8b08-bf24-4f59-8ce5-bc27c6bd9c17'
                    }
                }, {
                    'term': {
                        '_id': 'a57da16f-330a-4927-b532-ca013b6c83da'
                    }
                }]
            }
        }
    }

    resp = requests.post(url,
                         json=payload,
                         headers={'Accept': 'application/json'})
    resp.raise_for_status()

    return resp.json()


def _request_product(product_id: str):
    """Request AVISO's catalog product details."""
    url = os.path.join(AVISO_CATALOG_URL, 'records', product_id)

    resp = requests.get(url, headers={'Accept': 'application/json'})
    resp.raise_for_status()

    return resp.json()
