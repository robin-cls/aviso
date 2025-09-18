import pytest
import re
import logging
from aviso_client.catalog_parser.granule_discoverer import filter_granules, _parse_tds_layout, ConventionLoader, TDSIterable
from aviso_client.catalog_parser.models import AvisoProduct, ProductLayoutConfig, AvisoDataType
from ocean_tools.swath.io import AVISO_L3_LR_SSH_LAYOUT, FileNameConventionSwotL3
from ocean_tools.io import Layout, FileNameConvention, FileNameFieldString

@pytest.mark.parametrize('_id, version, subset', 
                         [('aa2927ad-d1d6-4867-89d3-1311bc11e6bb', '2.0.1', 'Basic'), 
                          ('8c961685-cecb-41d9-b2d9-2a22cdd3d0c2', '2.0.1', 'Expert'), 
                          ('de48c5b5-18f7-4829-ba0e-78f3dff047ac', '2.0.1', 'Unsmoothed')
                          ])
def test_parse_tds_layout(_id, version, subset):
    pl_conf = _parse_tds_layout(AvisoProduct(id=_id))
    assert isinstance(pl_conf, ProductLayoutConfig)
    
    assert pl_conf.id == _id
    assert pl_conf.default_filters == {'version': version, 'subset': subset}
    assert pl_conf.catalog_path == "dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/"
    assert pl_conf.title == f"Altimetry product SWOT Level-3 Low Rate SSH - {subset}"
    assert pl_conf.layout == AVISO_L3_LR_SSH_LAYOUT
    assert isinstance(pl_conf.convention, FileNameConventionSwotL3)
    
def test_filter_granules():
    # TODO complete test
    # urls = filter_granules(AvisoProduct(id='aa2927ad-d1d6-4867-89d3-1311bc11e6bb'))
    pass

class Test_ConventionLoader:
    @pytest.mark.parametrize('data_type, exp_convention, exp_layout', [(AvisoDataType.SWOT_L3_LR_SSH, FileNameConventionSwotL3, AVISO_L3_LR_SSH_LAYOUT)])
    def test_load(self, data_type, exp_convention, exp_layout):
        convention, layout = ConventionLoader().load(data_type)
        
        assert layout == exp_layout
        assert isinstance(convention, exp_convention)

class Test_TDSIterable:
    
    @pytest.fixture
    def tds_iterable(self):
        layout = Layout([FileNameConvention(re.compile('(?P<filter1>.*)'), [FileNameFieldString('filter1')], '{filter1!f}')])
        return TDSIterable(layout)

    @pytest.mark.parametrize('filter, exp_urls', [({}, ['https://tds.mock/dataset1.nc', 'https://tds.mock/vA/dataset2.nc', 'https://tds.mock/vB/dataset3.nc']), ({'filter1': 'A'}, ['https://tds.mock/dataset1.nc', 'https://tds.mock/vA/dataset2.nc']), ({'filter1': 'B'}, ['https://tds.mock/dataset1.nc', 'https://tds.mock/vB/dataset3.nc'])])
    def test_find(self, tds_iterable, filter, exp_urls):
        urls = tds_iterable.find('https://tds.mock/catalog.xml', **filter)
        
        assert urls == exp_urls
        
    @pytest.mark.parametrize('filter, exp_urls', [({'bad_filter': 'B'}, ['https://tds.mock/dataset1.nc', 'https://tds.mock/vA/dataset2.nc', 'https://tds.mock/vB/dataset3.nc'])])
    def test_find_bad_filter(self, tds_iterable, filter, exp_urls):
        with pytest.warns(UserWarning, match='Layout has been configured with unknown references \'{\'bad_filter\'}\'. They will be ignored.'):
            urls = tds_iterable.find('https://tds.mock/catalog.xml', **filter)
            assert urls == exp_urls
