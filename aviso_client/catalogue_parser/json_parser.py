from .models import AvisoCatalogue, AvisoProduct


def parse_catalogue_response(results: dict) -> AvisoCatalogue:
    products = []
    for record in results['hits']['hits']:
        product = AvisoProduct(
            id=record['_id'],
            title=record['_source']['resourceTitleObject']['default'],
            keywords=record['_source']['resourceAbstractObject']['default'])
        products.append(product)

    return AvisoCatalogue(products=products)


def parse_product_response(product_metadata: dict,
                           product: AvisoProduct) -> AvisoProduct:
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

    contentInfo = product_metadata['mdb:contentInfo']
    if 'mrc:MD_CoverageDescription' in contentInfo.keys():
        product.processing_level = contentInfo['mrc:MD_CoverageDescription'][
            'mrc:processingLevelCode']['mcc:MD_Identifier']['mcc:code'][
                'gco:CharacterString']['#text']
    else:
        product.processing_level = contentInfo['mrc:MI_CoverageDescription'][
            'mrc:processingLevelCode']['mcc:MD_Identifier']['mcc:code'][
                'gco:CharacterString']['#text']

    product.abstract = product_metadata['mdb:identificationInfo'][
        'mri:MD_DataIdentification']['mri:abstract']['gco:CharacterString'][
            '#text']
    product.credit = product_metadata['mdb:identificationInfo'][
        'mri:MD_DataIdentification']['mri:credit']['gco:CharacterString'][
            '#text']

    return product
