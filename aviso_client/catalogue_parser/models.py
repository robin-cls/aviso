from dataclasses import dataclass

import numpy as np


@dataclass
class AvisoProduct:
    """Product of the catalogue.

    Contains the product metadata.
    """
    id: str
    title: str | None = None
    keywords: str | None = None
    abstract: str | None = None
    processing_level: str | None = None
    credit: str | None = None
    organisation: str | None = None
    contact: str | None = None
    tds_catalogue_url: str | None = None  # https://tds%40odatis-ocean.fr:odatis@tds-odatis.aviso.altimetry.fr/thredds/catalog/L3/SWOT_KARIN-L3_LR_SSH.html
    spatial_representation_type: str | None = None
    resolution: str | None = None
    geographical_extent: tuple[float, float, float, float] | None = None
    temporal_extent: tuple[np.datetime64, np.datetime64] | None = None


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
