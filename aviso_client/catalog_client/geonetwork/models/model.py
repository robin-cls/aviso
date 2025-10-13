from dataclasses import dataclass

import numpy as np


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
    organisation: str | None = None
    contact: str | None = None
    resolution: str | None = None
    temporal_extent: tuple[np.datetime64, np.datetime64] | None = (None)
    geographic_extent: tuple[float, float, float, float] | None = (None)


@dataclass
class AvisoCatalog:
    """Catalog of the AVISO/ODATIS service."""

    products: list[AvisoProduct]
