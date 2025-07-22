from dataclasses import dataclass

@dataclass
class AvisoProduct:
    """Product of the catalogue.

    Contains the product metadata.
    """

    # Parameters depends on fields available in the catalogue

    #: Title of the product.
    title: str
    #: ID.
    id: str
    #: Abstract of the product.
    abstract: str
    #: Processing level of the product.
    processing_level: str | None = None
    #: Production center of the product.
    production_center: str = None
    #: Keywords of the product.
    keywords: list[str] | None = None
    # URL of the TDS Catalogue
    tds_catalogue_url: str | None = None # https://tds%40odatis-ocean.fr:odatis@tds-odatis.aviso.altimetry.fr/thredds/catalog/L3/SWOT_KARIN-L3_LR_SSH.html


@dataclass
class AvisoCatalogue:
    """Catalogue of the AVISO/ODATIS service."""
    products: list[AvisoProduct]


@dataclass
class Granule:

    dataset: str  # SWOT_L3_LR_SSH_Basic_004_171_20230927T213502_20230927T222628_v1.0.2.nc
    catalogue: str  # /thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v1_0_2/Basic/cycle_004/catalog.html
    data_size: int
    file_path: str  # dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v1_0_2/Basic/cycle_004/SWOT_L3_LR_SSH_Basic_004_171_20230927T213502_20230927T222628_v1.0.2.nc
