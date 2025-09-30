import enum
from dataclasses import dataclass

import numpy as np
from ocean_tools.io import FileNameConvention, Layout


@dataclass
class AvisoProduct:
    """Product of the catalog.

    Contains the product metadata.
    """
    id: str
    title: str | None = None
    short_name: str | None = None
    keywords: str | None = None
    abstract: str | None = None
    processing_level: str | None = None
    tds_catalog_url: str | None = None
    doi: str | None = None
    last_update: str | None = None
    last_version: str | None = None
    credit: str | None = None
    # Not set
    contact: str | None = None  # "aviso@altimetry.fr"
    resolution: str | None = None  # "0.25"
    geographical_extent: tuple[
        float, float, float,
        float] | None = None  # "-180.00, 180.00, -80.00, 90.00"
    temporal_extent: tuple[np.datetime64,
                           np.datetime64] | None = None  # "2023-03-29"/None


@dataclass
class AvisoCatalog:
    """Catalog of the AVISO/ODATIS service."""
    products: list[AvisoProduct]


@dataclass
class ProductLayoutConfig:
    """Configuration of a product layout.

    Contains the product metadata.
    """
    id: str
    title: str
    convention: FileNameConvention
    layout: Layout
    catalog_path: str
    default_filters: dict
