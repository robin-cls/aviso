from .models.dataclasses import AvisoCatalog, AvisoProduct
from .models.catalog_resp_model import AvisoCatalogModel
from pydantic import TypeAdapter

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
        product = AvisoProduct(id=record.field_id, title=record.field_source.resourceTitleObject.default, keywords=record.field_source.resourceAbstractObject.default)
        
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

def parse_product_response(meta: dict, product: AvisoProduct) -> AvisoProduct:
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

    identifier = meta['mdb:identificationInfo']['mri:MD_DataIdentification'][
        'mri:citation']['cit:CI_Citation']['cit:identifier']
    if isinstance(identifier, list):
        identifier = identifier[0]
    product.last_version = identifier['mcc:MD_Identifier']['mcc:version'][
        'gco:CharacterString']['#text']

    transferOptions = meta['mdb:distributionInfo']['mrd:MD_Distribution'][
        'mrd:transferOptions']
    if isinstance(transferOptions, list):
        transferOptions = transferOptions[0]
    online = transferOptions['mrd:MD_DigitalTransferOptions']['mrd:onLine']

    for online_resource in online:
        if online_resource is not None:
            if online_resource['cit:CI_OnlineResource']['cit:description'][
                    'gco:CharacterString']['#text'] == 'THREDDS':
                tds_url = online_resource['cit:CI_OnlineResource'][
                    'cit:linkage']['gco:CharacterString']['#text']

    product.tds_catalog_url = tds_url

    contentInfo = meta['mdb:contentInfo']
    if 'mrc:MD_CoverageDescription' in contentInfo.keys():
        product.processing_level = contentInfo['mrc:MD_CoverageDescription'][
            'mrc:processingLevelCode']['mcc:MD_Identifier']['mcc:code'][
                'gco:CharacterString']['#text']
    else:
        product.processing_level = contentInfo['mrc:MI_CoverageDescription'][
            'mrc:processingLevelCode']['mcc:MD_Identifier']['mcc:code'][
                'gco:CharacterString']['#text']

    product.abstract = meta['mdb:identificationInfo'][
        'mri:MD_DataIdentification']['mri:abstract']['gco:CharacterString'][
            '#text']
    product.credit = meta['mdb:identificationInfo'][
        'mri:MD_DataIdentification']['mri:credit']['gco:CharacterString'][
            '#text']

    return product
