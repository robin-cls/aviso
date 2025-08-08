import os
import logging
import yaml

logger = logging.getLogger(__name__)

from .models import AvisoProduct, Layout, PathFilter, TDSWalkable
from aviso_client.ocean_tools.io import FileNameFilterer, FileNameConvention
from aviso_client.ocean_tools.swath.io import FilenameConventionLoader, FilenameConventionName

TDS_LAYOUT_CONFIG = os.path.join(os.path.dirname(__file__), 'resources',
                                 'tds_layout.yaml')

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
    # Get product layout on TDS
    product_layout = _get_product_layout(product)
    
    # Get filename convention
    convention = _get_filename_convention(product)
    
    # Filter granules
    filterer = FileNameFilterer(parser=convention, walkable=TDSWalkable(product_layout))
    granules = filterer.list(**filters)
    if granules.empty:
        return []
    return [path for _, path in granules.filename]


def _get_product_layout(product: AvisoProduct) -> Layout:
    """ Parse resources/tds_layout.yaml to retrieve the product layout information """
    with open(TDS_LAYOUT_CONFIG) as f:
        
        tds_layout = yaml.safe_load(f)
        product_layout = tds_layout[product.id]
        
        return Layout(
            path_pattern=product_layout['catalog_path_pattern'],
            path_filters=[PathFilter(name=f['name'], repr_t=f['repr']) for f in product_layout['path_filters']],
            optional_path_filters=[PathFilter(name=f['name'], repr_t=f['repr']) for f in product_layout['optional_path_filters']]
        )
        
def _get_filename_convention(product: AvisoProduct) -> FileNameConvention:
    """ Parse resources/tds_layout.yaml to retrieve the convention information """
    with open(TDS_LAYOUT_CONFIG) as f:
        
        tds_layout = yaml.safe_load(f)
        product_layout = tds_layout[product.id]
        
        return FilenameConventionLoader().load(FilenameConventionName.from_str(product_layout['filename_convention']))