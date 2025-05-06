from typing import Mapping, Union
from .fundamental_unit import FundamentalUnit

RealLike = Union[int, float]
UnitDict = Mapping[FundamentalUnit, RealLike]