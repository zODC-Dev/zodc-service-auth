from typing import TypeVar

from sqlalchemy.orm import InstrumentedAttribute

_T = TypeVar("_T")


def attr(instance: _T) -> InstrumentedAttribute[_T]:
    """Return the attribute of the instance"""
    return instance  # type: ignore
