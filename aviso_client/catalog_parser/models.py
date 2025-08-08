from dataclasses import dataclass, field

import os

import numpy as np
from typing import TypeVar, Generic

from siphon.catalog import TDSCatalog

from pathlib import Path

from aviso_client.ocean_tools.io import ILayout, IWalkable

T = TypeVar('T')

TDS_CATALOG_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/catalog/'

@dataclass
class AvisoProduct:
    """Product of the catalog.

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
    tds_catalog_url: str | None = None  # https://tds%40odatis-ocean.fr:odatis@tds-odatis.aviso.altimetry.fr/thredds/catalog/L3/SWOT_KARIN-L3_LR_SSH.html
    spatial_representation_type: str | None = None
    resolution: str | None = None
    geographical_extent: tuple[float, float, float, float] | None = None
    temporal_extent: tuple[np.datetime64, np.datetime64] | None = None


@dataclass
class AvisoCatalog:
    """Catalog of the AVISO/ODATIS service."""
    products: list[AvisoProduct]

@dataclass
class PathFilter(Generic[T]):
    name: str  = field(default_factory=str) #cycle_number
    repr_t: str  = field(default_factory=str) #cycle_{cycle_number:03}
    
    def to_string(self, value) -> str:
        return self.repr_t.format(**{self.name:value})
    
    def validate(self, filter:T, name:str)-> bool:
        if isinstance(filter, list):
            for f in filter:
                if name == self.to_string(f):
                    return True
        if name == self.to_string(filter):
            return True
        return False
    
@dataclass
class Layout(ILayout):
    path_pattern: str = field(default_factory=str)
    path_filters: list[PathFilter] = field(default_factory=list)
    optional_path_filters: list[PathFilter] =  field(default_factory=list)
    
    def build_path(self, **filters):
        # TODO Verify mandatory filters are present in filters
        # Build base path with all filters
        path = _safe_format_path(self.path_pattern, **filters)
        return os.path.join(TDS_CATALOG_BASE_URL, path, 'catalog.xml')
        
    def validate_path(self, path:str, filters: dict):
        # Check if the path is valid using optional filters
        for f in self.optional_path_filters:
            if f.validate(filters[f.name], path):
                return True
        return False


class TDSWalkable(IWalkable):
    
    def walk(self, **filters):
        """
        Walk the structure using provided filters.
        """
        # walk with filters
        base_path = self.layout.build_path(**filters)
        yield from tds_walk(base_path, self.layout, 2, **filters)
        
def _safe_format_path(path_template: str, **values):
    """
    Format a path with provided values
    Ignore parts raising a KeyError.
    """
    path = Path(path_template)
    formatted_parts = []

    for part in path.parts:
        try:
            formatted_parts.append(part.format(**values))
        except KeyError:
            continue

    return Path(*formatted_parts)

def tds_walk(url, layout, depth=2, **filters):
    """Return a generator walking a THREDDS data catalog for datasets.

    Parameters
    ----------
    cat : TDSCatalog
      THREDDS catalog.
    depth : int
      Maximum recursive depth. Setting 0 will return only datasets within the top-level catalog. If None,
      depth is set to 1000.
    """
    cat = TDSCatalog(url)
    for ds_name, ds in cat.datasets.items():
        yield (ds_name, ds.access_urls["HTTPServer"])
    if depth is None:
        depth = 1000

    if depth > 0:
        for name, ref in cat.catalog_refs.items():
            # If name corresponds to filters, continue
            # ex: name=cycle_001
            if layout.validate_path(name, filters):
            # Each catalog_refs should have (name, ref) and it should be possible to follow ref with child = ref.follow()
            # but there is a name marker missing somewhere in odatis TDS catalog.xml so it's not possible to follow a ref
            # So we use the href and create a new TDSCatalog object with it
            # ex: ref.href=https://tds-odatis.aviso.altimetry.fr/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v1_0_1/Unsmoothed/cycle_001/catalog.xml
            
                yield from tds_walk(ref.href, depth=depth - 1)