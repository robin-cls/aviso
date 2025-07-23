import os

import requests

from .granule_discoverer import filter_granules
from .json_parser import parse_catalogue_response, parse_product_response
from .models import AvisoCatalogue, AvisoProduct

AVISO_CATALOGUE_URL = 'https://sextant.ifremer.fr/geonetwork/srv/api'


def fetch_catalogue() -> AvisoCatalogue:
    resp = _request_catalogue()
    catalog = parse_catalogue_response(resp)
    return catalog


def get_details(product_name: str) -> AvisoProduct:
    product = _get_product(product_name)
    resp = _request_product(product.id)
    product = parse_product_response(resp, product)
    return product


def _request_catalogue() -> dict:
    # request catalogue : filter on CDS-AVISO and Swot
    url = os.path.join(AVISO_CATALOGUE_URL, 'search/records/_search')
    payload = {
        'from': 0,
        'size': 20,
        'query': {
            'match': {
                'th_odatis_centre_donnees.default': 'CDS-AVISO'
            },
            'match': {
                'platforms': 'SWOT'
            }
        }
    }

    resp = requests.post(url,
                         json=payload,
                         headers={'Accept': 'application/json'})
    resp.raise_for_status()

    return resp.json()


def _get_product(product_name: str) -> str:
    # search for a product in the catalogue
    catalogue = fetch_catalogue()
    for p in catalogue.products:
        if p.title == product_name:
            return p
    raise ValueError(f'Invalid product name "{product_name}"')


def _request_product(product_id: str):
    # GET AVISO_CATALOGUE_URL+"/records/"+product_id
    url = os.path.join(AVISO_CATALOGUE_URL, 'records', product_id)
    resp = requests.get(url, headers={'Accept': 'application/json'})
    return resp.json()


def search_granules(product_name: str, **filters) -> list[str]:
    product = _get_product(product_name)
    # search for granules
    return filter_granules(product, **filters)
