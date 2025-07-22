import os

import requests

from .granule_discoverer import filter_granules
from .models import AvisoCatalogue, AvisoProduct

AVISO_CATALOGUE_URL = 'https://sextant.ifremer.fr/geonetwork/srv/api'


def fetch_catalogue() -> AvisoCatalogue:
    resp = _request_catalogue()
    catalog = _parse_catalogue_response(resp)
    return catalog


def get_details(product_name: str) -> AvisoProduct:
    product = _get_product(product_name)
    resp = _request_product(product.id)
    product = _parse_product_response(resp, product)
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


def _parse_catalogue_response(results: dict):
    products = []
    for record in results['hits']['hits']:
        product = AvisoProduct(
            id=record['_id'],
            title=record['_source']['resourceTitleObject']['default'],
            abstract=record['_source']['resourceAbstractObject']['default'])
        products.append(product)

    return AvisoCatalogue(products=products)


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


def _parse_product_response(product_metadata: dict, product: AvisoProduct):
    transferOptions = product_metadata['mdb:distributionInfo'][
        'mrd:MD_Distribution']['mrd:transferOptions']
    if isinstance(transferOptions, list):
        online = transferOptions[0]['mrd:MD_DigitalTransferOptions'][
            'mrd:onLine']
    else:
        online = transferOptions['mrd:MD_DigitalTransferOptions']['mrd:onLine']

    for online_resource in online:
        if online_resource is not None:
            if online_resource['cit:CI_OnlineResource']['cit:description'][
                    'gco:CharacterString']['#text'] == 'THREDDS':
                tds_url = online_resource['cit:CI_OnlineResource'][
                    'cit:linkage']['gco:CharacterString']['#text']

    product.tds_catalogue_url = tds_url

    return product


def search_granules(product_name: str, **filters) -> list[str]:
    product = _get_product(product_name)
    # search for granules
    return filter_granules(product.tds_catalogue_url, **filters)
