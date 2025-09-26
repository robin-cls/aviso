import logging
import os
import typing as tp
import warnings
from importlib import import_module
from pathlib import Path

import yaml
from ocean_tools.io import FileDiscoverer, ITreeIterable, Layout
from siphon.catalog import TDSCatalog

from .models.dataclasses import (
    AvisoProduct,
    ProductLayoutConfig,
)

logger = logging.getLogger(__name__)

TDS_CATALOG_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/catalog/'

TDS_LAYOUT_CONFIG = Path(__file__).parent / 'resources' / 'tds_layout.yaml'


class TDSIterable(ITreeIterable):
    """List files or links in a TDS Server.

    Parameters
    ----------
    layout
        Layout allowing to guess the tree structure and eventually discard some
        branches along the search
    """

    def __init__(self, layout: Layout | None = None):
        super().__init__(layout)

    def find(self,
             root: str,
             detail: bool = False,
             **filters: tp.Any) -> tp.Iterator[str | dict[str, str]]:

        if len(filters) > 0 and self.layout is None:
            msg = ('Filters %s have been defined for the file '
                   'system tree walk, but no layout is configured. These '
                   'filters will be ignored', filters.keys())
            warnings.warn(msg)

        if self.layout is not None:
            self.layout.set_filters(**filters)

        return self._find(root, **filters)

    def _find(self, url: str, level: int = 0, **filters):
        cat = TDSCatalog(url)

        results = [d.access_urls['HTTPServer'] for d in cat.datasets.values()]

        for folder, ref in cat.catalog_refs.items():
            # If name doesn't correspond to filters, continue
            if self.layout is not None and not self.layout.test(level, folder):
                logger.debug('Ignore folder %s', folder)
                continue

            next_level = level + 1

            # Each catalog_refs should have (name, ref) and it should be possible to follow ref with child = ref.follow()
            # but there is a "name" marker missing somewhere in odatis TDS catalog.xml so it's not possible to follow a ref
            # So we use the href and create a new TDSCatalog object with it
            # ex: ref.href=https://tds-odatis.aviso.altimetry.fr/thredds/catalog/dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v1_0_1/Unsmoothed/cycle_001/catalog.xml
            results += self._find(ref.href, next_level, **filters)

        return results


def filter_granules(product: AvisoProduct, **filters) -> list[str]:
    """Filter granules of a product in AVISO's Thredds Data Server.

    Parameters
    ----------
    product
        the aviso product
    **filters
        filters for files selection

    Returns
    -------
    list[str]
        the urls of the granules corresponding to the provided filters
    """
    # Get TDS product layout
    product_layout_conf = _parse_tds_layout(product)

    # Build TDS catalog URL
    tds_url = os.path.join(TDS_CATALOG_BASE_URL,
                           product_layout_conf.catalog_path, 'catalog.xml')

    # Create the file discoverer for this TDS catalog
    file_discoverer = FileDiscoverer(
        parser=product_layout_conf.convention,
        iterable=TDSIterable(layout=product_layout_conf.layout))
    filters = {**product_layout_conf.default_filters, **filters}

    granules = file_discoverer.list(path=tds_url, **filters)

    return granules.filename


def _load_convention_layout(granule_discovery, data_type):
    if not data_type in granule_discovery:
        raise KeyError(
            f'The data type {data_type} is missing from the tds_layout|granule_discovery configuration.'
        )
    convention, layout = granule_discovery[data_type]

    module = import_module('ocean_tools.swath.io')
    convention_obj, layout_obj = getattr(module, convention)(), getattr(
        module, layout)
    return convention_obj, layout_obj


def _parse_tds_layout(product: AvisoProduct) -> ProductLayoutConfig:
    """Parse resources/tds_layout.yaml to retrieve the layout information.

    The yaml should have a 'products' and a 'granule_discovery'
    sections.
    """
    with open(TDS_LAYOUT_CONFIG) as f:

        tds_layout = yaml.safe_load(f)

        products_tds_layout = tds_layout['products']
        if not product.id in products_tds_layout:
            raise KeyError(
                f'The product {product.title} - {product.id} is missing from the tds_layout configuration file.'
            )
        product_layout = products_tds_layout[product.id]

        granule_discovery = tds_layout['granule_discovery']
        data_type = product_layout['data_type']
        convention_obj, layout_obj = _load_convention_layout(
            granule_discovery, data_type)

        if 'filters' not in product_layout:
            product_layout['filters'] = {}

        return ProductLayoutConfig(id=product.id,
                                   title=product_layout['title'],
                                   convention=convention_obj,
                                   layout=layout_obj,
                                   catalog_path=product_layout['catalog_path'],
                                   default_filters=product_layout['filters'])
