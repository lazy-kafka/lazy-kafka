from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)
S = TypeVar("S", covariant=True)

StrLike = TypeVar("StrLike", covariant=True, bound=str)
"""Type for str derived types e.g.: topic.Topic."""

@runtime_checkable
class ProviderProtocol[T, S](Protocol):
    async def aget_details(self, *args, **kwargs) -> T:
        ...

    async def asubjects(self, *args, **kwargs) -> S:
        ...

