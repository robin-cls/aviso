from enum import Enum, auto


class Upstream(Enum):
    """Upstream enum."""
    OLCI = auto()
    MULTI = auto()


class ProductLevel(Enum):
    """Product level enum."""
    L1A = auto()
    L1B = auto()
    L2 = auto()
    L3 = auto()
    L4 = auto()


class Delay(Enum):
    NRT = auto()
    DT = auto()
    MY = auto()
    MYINT = auto()


class AcquisitionMode(Enum):
    IW = auto()
    EW = auto()
    WV = auto()
    SM = auto()


class S1AOWIProductType(Enum):
    SW = auto()
    GS = auto()


class S1AOWISlicePostProcessing(Enum):

    CC = auto()
    CM = auto()
    OCN = auto()
