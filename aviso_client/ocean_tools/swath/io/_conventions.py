import enum
import re

import numpy as np

from aviso_client.ocean_tools.io import (
    CaseType,
    FileNameConvention,
    FileNameFieldDateDelta,
    FileNameFieldDateJulian,
    FileNameFieldDateJulianDelta,
    FileNameFieldDatetime,
    FileNameFieldEnum,
    FileNameFieldInteger,
    FileNameFieldPeriod,
    FileNameFieldString,
)
from aviso_client.ocean_tools.missions import MissionsPhases

from ._definitions import (
    AcquisitionMode,
    Delay,
    ProductLevel,
    S1AOWIProductType,
    S1AOWISlicePostProcessing,
    Upstream,
)
from ._products import L2VersionField, ProductSubset

# This pattern is used for Swot data preprocessing
SWOT_PATTERN = re.compile(
    r'(.*)_(?P<cycle_number>\d{3})_(?P<pass_number>\d{3})_(.*)')

SWOT_L2_PATTERN = re.compile(
    r'SWOT_(?P<level>.*)_LR_SSH_(?P<subset>.*)_(?P<cycle_number>\d{3})_(?P<pass_number>\d{3})_'
    r'(?P<time>\d{8}T\d{6}_\d{8}T\d{6})_(?P<version>P[I|G][A-Z]\d{1}_\d{2}).nc'
)

SWOT_L3_PATTERN = re.compile(
    r'SWOT_(?P<level>.*)_LR_SSH_(?P<subset>.*)_(?P<cycle_number>\d{3})_(?P<pass_number>\d{3})_'
    r'(?P<time>\d{8}T\d{6}_\d{8}T\d{6})_v(?P<version>.*).nc')

SST_PATTERN = re.compile(
    r'(?P<time>\d{8}\d{6})-IFR-L3S_GHRSST-SSTfnd-ODYSSEA-GLOB_010-v02.1-fv01.0.nc'
)

CHL_PATTERN = re.compile(
    r'(?P<time>\d{8})_cmems_obs-oc_glo_bgc-plankton_(?P<delay>.*)_(?P<level>l\d{1})(-gapfree){0,1}-(?P<upstream>olci|multi)-4km_P1D.nc'
)

GRIDDED_SLA_PATTERN = re.compile(
    r'(?P<delay>.*)_(.*)_allsat_phy_l4_(?P<time>(\d{8})|(\d{8}T\d{2}))_(?P<production_date>\d{8}).nc'
)

INTERNAL_SLA_PATTERN = re.compile(r'msla_oer_merged_h_(?P<date>\d{5}).nc')

DAC_PATTERN = re.compile(r'dac_dif_((\d+)days_){0,1}(?P<time>\d{5}_\d{2}).nc')

OHC_PATTERN = re.compile(
    r'OHC-NAQG3_v1r0_blend_s(.*)_e(.*)_c(?P<time>\d{8})(.*).nc')

SWH_PATTERN = re.compile(
    r'global_vavh_l3_rt_(?P<mission>.*)_(?P<time>\d{8}T\d{6}_\d{8}T\d{6})_(?P<production_date>\d{8}T\d{6}).nc'
)

S1AOWI_PATTERN = re.compile(
    r's1a-(?P<acquisition_mode>.*)-owi-(?P<slice_post_processing>.*)-(?P<time>\d{8}t\d{6}-\d{8}t\d{6})-(?P<resolution>\d{6})-(?P<orbit>\d{6})_(?P<product_type>.*).nc'
)

ERA5_PATTERN = re.compile(r'reanalysis-era5-single-levels_(?P<time>\d{8}).nc')

MUR_PATTERN = re.compile(
    r'(?P<time>\d{8}\d{6})-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc')

L3_NADIR_PATTERN = re.compile(
    r'(?P<delay>.*)_global_(?P<mission>.*)_(hr_){0,1}phy_(aux_){0,1}(?P<product_level>l3)_(?P<resolution>\d+)*(hz_)*(?P<time>\d{8})_(?P<production_date>\d{8}).nc'
)

L2_NADIR_PATTERN = re.compile(
    r'SWOT_(GPN|IPN)_2PfP(?P<cycle_number>\d{3})_(?P<pass_number>\d{3})_(?P<time>\d{8}_\d{6}_\d{8}_\d{6}).nc'
)

DESCRIPTIONS = {
    'cycle_number': ('Cycle number of the half orbit. A half orbit is '
                     'identified using a cycle number and a pass number.'),
    'pass_number': ('Pass number of the half orbit. A half orbit is '
                    'identified using a cycle number and a pass number.'),
    'time':
    'Period covered by the file.',
    'level':
    'Product level of the data.',
    'subset':
    ('Subset of the LR Karin products. The Basic and Expert subsets '
     'are defined on a reference grid, opening the possibility of stacking the '
     'files, whereas the Unsmoothed subset is defined on a different grid for '
     'each cycle.'),
    'production_date':
    ('Production date of a given file. The same granule is '
     'regenerated multiple times with updated corrections. Hence'
     ' there can be multiple files for the same period, but with'
     ' a different production date.'),
    'upstream':
    'Upstream.',
    'delay':
    'Delay.'
}


class FileNameConventionSwotL2(FileNameConvention):
    """Swot LR L2 datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=SWOT_L2_PATTERN,
            fields=[
                FileNameFieldInteger('cycle_number',
                                     description=DESCRIPTIONS['cycle_number']),
                FileNameFieldInteger('pass_number',
                                     description=DESCRIPTIONS['pass_number']),
                FileNameFieldPeriod('time',
                                    '%Y%m%dT%H%M%S',
                                    '_',
                                    description=DESCRIPTIONS['time']),
                FileNameFieldEnum('level',
                                  ProductLevel,
                                  description=DESCRIPTIONS['level']),
                FileNameFieldEnum('subset',
                                  ProductSubset,
                                  description=DESCRIPTIONS['subset']),
                L2VersionField('version')
            ],
            generation_string=
            'SWOT_{level!f}_LR_SSH_{subset!f}_{cycle_number:>03d}_{pass_number:>03d}_{time!f}_{version!f}.nc'
        )


class FileNameConventionSwotL3(FileNameConvention):
    """Swot LR L3 datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=SWOT_L3_PATTERN,
            fields=[
                FileNameFieldInteger('cycle_number',
                                     description=DESCRIPTIONS['cycle_number']),
                FileNameFieldInteger('pass_number',
                                     description=DESCRIPTIONS['pass_number']),
                FileNameFieldPeriod('time',
                                    '%Y%m%dT%H%M%S',
                                    '_',
                                    description=DESCRIPTIONS['time']),
                FileNameFieldEnum('level',
                                  ProductLevel,
                                  description=DESCRIPTIONS['level']),
                FileNameFieldEnum('subset',
                                  ProductSubset,
                                  description=DESCRIPTIONS['subset']),
                FileNameFieldString(
                    'version',
                    description=(
                        'Version of the L3_LR_SSH Swot product. This is'
                        ' a tri-number version x.y.z, where x denotes a'
                        ' major change in the product, y a minor change'
                        ' and z a fix.')),
            ],
            generation_string=
            'SWOT_{level!f}_LR_SSH_{subset!f}_{cycle_number:>03d}_{pass_number:>03d}_{time!f}_v{version}.nc'
        )


class FileNameConventionSST(FileNameConvention):
    """Sea Surface Temperature datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=SST_PATTERN,
            fields=[
                FileNameFieldDatetime('time',
                                      '%Y%m%d%H%M%S',
                                      description=DESCRIPTIONS['time'])
            ],
            generation_string=
            '{time!f}-IFR-L3S_GHRSST-SSTfnd-ODYSSEA-GLOB_010-v02.1-fv01.0.nc')


class FileNameConventionCHL(FileNameConvention):
    """Chlorophyl datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=CHL_PATTERN,
            fields=[
                FileNameFieldDateDelta('time',
                                       '%Y%m%d',
                                       np.timedelta64(1, 'D'),
                                       description=DESCRIPTIONS['time']),
                FileNameFieldEnum('delay',
                                  Delay,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=DESCRIPTIONS['delay']),
                FileNameFieldEnum('level',
                                  ProductLevel,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=DESCRIPTIONS['level']),
                FileNameFieldEnum('upstream',
                                  Upstream,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=DESCRIPTIONS['upstream'])
            ])


class FileNameConventionGriddedSLA(FileNameConvention):
    """Gridded SLA datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=GRIDDED_SLA_PATTERN,
            fields=[
                FileNameFieldEnum('delay',
                                  Delay,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=DESCRIPTIONS['delay']),
                FileNameFieldDateDelta('time', ['%Y%m%d', '%Y%m%dT%H'],
                                       np.timedelta64(1, 'D'),
                                       description=DESCRIPTIONS['time']),
                FileNameFieldDatetime(
                    'production_date',
                    '%Y%m%d',
                    description=DESCRIPTIONS['production_date']),
            ])


class FileNameConventionGriddedSLAInternal(FileNameConvention):

    def __init__(self):
        super().__init__(regex=INTERNAL_SLA_PATTERN,
                         fields=[
                             FileNameFieldDateJulianDelta(
                                 'date',
                                 reference=np.datetime64('1950-01-01T00'),
                                 delta=np.timedelta64(1, 'D'),
                                 description=DESCRIPTIONS['time'])
                         ],
                         generation_string='msla_oer_merged_h_{date!f}.nc')


class FileNameConventionDAC(FileNameConvention):

    def __init__(self):
        super().__init__(regex=DAC_PATTERN,
                         fields=[
                             FileNameFieldDateJulian(
                                 'time',
                                 reference=np.datetime64('1950-01-01T00'),
                                 julian_day_format='days_hours')
                         ],
                         generation_string='dac_dif_{time!f}.nc')


class FileNameConventionOHC(FileNameConvention):

    def __init__(self):
        super().__init__(regex=OHC_PATTERN,
                         fields=[
                             FileNameFieldDatetime(
                                 'time',
                                 '%Y%m%d',
                                 description=DESCRIPTIONS['time']),
                         ])


class FileNameConventionSWH(FileNameConvention):

    def __init__(self):
        super().__init__(
            regex=SWH_PATTERN,
            fields=[
                FileNameFieldEnum(
                    'mission',
                    MissionsPhases,
                    description=('Altimetry mission in the file.')),
                FileNameFieldPeriod('time',
                                    '%Y%m%dT%H%M%S',
                                    '_',
                                    description=DESCRIPTIONS['time']),
                FileNameFieldDatetime(
                    'production_date',
                    '%Y%m%dT%H%M%S',
                    description=DESCRIPTIONS['production_date']),
            ],
            generation_string=
            'global_vavh_l3_rt_{mission!f}_{time!f}_{production_date!f}.nc')


class FileNameConventionS1AOWI(FileNameConvention):

    def __init__(self):
        super().__init__(
            regex=S1AOWI_PATTERN,
            fields=[
                FileNameFieldEnum('acquisition_mode',
                                  AcquisitionMode,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=('Acquisition mode.')),
                FileNameFieldEnum('slice_post_processing',
                                  S1AOWISlicePostProcessing,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=('Slices post-processing.')),
                FileNameFieldPeriod('time',
                                    '%Y%m%dt%H%M%S',
                                    '-',
                                    description=DESCRIPTIONS['time']),
                FileNameFieldInteger(
                    'resolution',
                    description=(
                        'SAR Ocean surface wind Level-2 product resolution.')),
                FileNameFieldInteger('orbit', description=('Orbit number')),
                FileNameFieldEnum('product_type',
                                  S1AOWIProductType,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=('Product type.')),
            ],
            generation_string=
            's1a-{acquisition_mode!f}-owi-{slice_post_processing!f}-{time!f}-{resolution:>06d}-{orbit:>06d}_{product_type!f}.nc'
        )


class FileNameConventionERA5(FileNameConvention):

    def __init__(self):
        super().__init__(
            regex=ERA5_PATTERN,
            fields=[
                FileNameFieldDatetime('time',
                                      '%Y%m%d',
                                      description=DESCRIPTIONS['time'])
            ],
            generation_string='reanalysis-era5-single-levels_{time!f}.nc')


class FileNameConventionMUR(FileNameConvention):

    def __init__(self):
        super().__init__(
            regex=MUR_PATTERN,
            fields=[
                FileNameFieldDatetime('time',
                                      '%Y%m%d%H%M%S',
                                      description=DESCRIPTIONS['time'])
            ],
            generation_string=
            '{time!f}-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc')


class FileNameConventionL2Nadir(FileNameConvention):
    """L2 Nadir datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=L2_NADIR_PATTERN,
            fields=[
                FileNameFieldInteger('cycle_number',
                                     description=DESCRIPTIONS['cycle_number']),
                FileNameFieldInteger('pass_number',
                                     description=DESCRIPTIONS['pass_number']),
                FileNameFieldPeriod('time',
                                    '%Y%m%d_%H%M%S',
                                    '_',
                                    description=DESCRIPTIONS['time']),
            ])


class FileNameConventionL3Nadir(FileNameConvention):
    """L3 Nadir datafiles parser."""

    def __init__(self):
        super().__init__(
            regex=L3_NADIR_PATTERN,
            fields=[
                FileNameFieldEnum('delay',
                                  Delay,
                                  case_type=CaseType.upper,
                                  case_type_encoded=CaseType.lower,
                                  description=DESCRIPTIONS['delay']),
                FileNameFieldDateDelta('time',
                                       '%Y%m%d',
                                       np.timedelta64(1, 'D'),
                                       description=DESCRIPTIONS['time']),
                FileNameFieldDatetime(
                    'production_date',
                    '%Y%m%d',
                    description=
                    ('Production date of a given file. The same granule is '
                     'regenerated multiple times with updated corrections. Hence'
                     ' there can be multiple files for the same period, but with'
                     ' a different production date.')),
                FileNameFieldEnum(
                    'mission',
                    MissionsPhases,
                    description=('Altimetry mission in the file.')),
                FileNameFieldEnum('product_level',
                                  ProductLevel,
                                  'upper',
                                  description='Product level of the data.'),
                FileNameFieldInteger(
                    'resolution',
                    default=1,
                    description=
                    ('Data resolution. Nadir products may be sampled at 1Hz, 5Hz'
                     ' or 20Hz depending on the level and dataset considered.'
                     ))
            ])
