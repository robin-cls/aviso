from pydantic import TypeAdapter

from .models.catalog_resp_model import AvisoCatalogModel
from .models.dataclasses import AvisoCatalog, AvisoProduct
from .models.product_resp_model import AvisoProductModel


def parse_catalog_response(results: dict) -> AvisoCatalog:
    """Parses the response of AVISO's catalog to a fetching request.

    Parameters
    ----------
    results
        the dictionary representing the json catalog's response

    Returns
    -------
    AvisoCatalog
        the object resulting from the parsing
    """
    adapter = TypeAdapter(AvisoCatalogModel)
    catalog = adapter.validate_python(results)

    products = []
    for record in catalog.hits.hits:
        product = AvisoProduct(
            id=record.field_id,
            title=record.field_source.resourceTitleObject.default,
            keywords=record.field_source.resourceAbstractObject.default)

        for link in record.field_source.link:
            if link.descriptionObject is not None:
                if link.descriptionObject.default == 'THREDDS':
                    product.tds_catalog_url = link.urlObject.default

                    if link.nameObject is not None:
                        product.short_name = link.nameObject.default

            if link.protocol == 'DOI':
                product.doi = link.urlObject.default

        product.last_update = record.field_source.resourceDate[-1].date

        products.append(product)

    return AvisoCatalog(products=products)


def parse_product_response(meta: dict,
                           aviso_product: AvisoProduct) -> AvisoProduct:
    """Parses the response of AVISO's catalog to a product request.

    Parameters
    ----------
    meta
        the json to parse
    product
        the product object to fill in

    Returns
    -------
    AvisoProduct
        the object resulting from the parsing
    """
    adapter = TypeAdapter(AvisoProductModel)
    product = adapter.validate_python(meta)

    aviso_product.last_version = product.get_last_version()
    aviso_product.tds_catalog_url = product.get_tds_url()
    aviso_product.processing_level = product.get_processing_level()
    aviso_product.abstract = product.get_abstract()
    aviso_product.credit = product.get_credit()

    return aviso_product
