from __future__ import annotations


from typing import Protocol, TypeVar, runtime_checkable, Generic

T = TypeVar("T", covariant=True)
S = TypeVar("S", covariant=True)

@runtime_checkable
class ProviderProtocol(Protocol, Generic[T,S]):
    async def aget_details(self, *args, **kwargs) -> T:
        ...

    async def asubjects(self, *args, **kwargs) -> S:
        ...
