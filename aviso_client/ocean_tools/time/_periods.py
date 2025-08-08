from __future__ import annotations

import dataclasses as dc

import numpy as np


@dc.dataclass(frozen=True)
class Period:
    """Period representation.

    Parameters
    ----------
    start: np.datetime64
        date representing the start of the period
    stop: np.datetime64
        date representing the end of the period
    include_start: boolean
         inclusive (True) or strict (False) start selection
    include_stop: boolean
         inclusive (True) or strict (False) end selection
    """
    start: np.datetime64
    stop: np.datetime64
    include_start: bool = True
    include_stop: bool = True

    @property
    def center(self) -> np.datetime64:
        return self.start + np.timedelta64((self.stop - self.start).item() / 2)

    def _equals(self, time: np.datetime64):
        return self.start == time or self.stop == time

    def _include(self, time: np.datetime64, include: bool):
        if self.start == time: return self.include_start and include
        if self.stop == time: return self.include_stop and include

    def intersects(self,
                   times: np.datetime64 | Period,
                   include_time: bool = True):
        if isinstance(times, np.datetime64):
            return (self.start <= times if
                    (self.include_start and include_time) else self.start <
                    times) and (times <= self.stop if
                                (self.include_stop
                                 and include_time) else times < self.stop)

        if self._equals(times.start):
            if self._include(times.start, times.include_start):
                return True
            if self._equals(times.stop):
                return True
            if self.intersects(times.stop):
                return True
            return times.intersects(self.start,
                                    self.include_start) | times.intersects(
                                        self.stop, self.include_stop)

        if self._equals(times.stop):
            if self._include(times.stop, times.include_stop):
                return True
            if self.intersects(times.start):
                return True
            return times.intersects(self.start,
                                    self.include_start) | times.intersects(
                                        self.stop, self.include_stop)

        return (self.intersects(times.start) | self.intersects(times.stop)
                | times.intersects(self.start, self.include_start)
                | times.intersects(self.stop, self.include_stop))

    def __le__(self, obj: Period) -> bool:
        return self.start <= obj.start

    def __ge__(self, obj: Period) -> bool:
        return self.stop >= obj.stop

    def __lt__(self, obj: Period) -> bool:
        return self.start < obj.start

    def __gt__(self, obj: Period) -> bool:
        return self.stop > obj.stop

    def __repr__(self):
        return f"{'[' if self.include_start else ']'}{self.start}, {self.stop}{']' if self.include_stop else '['}"
