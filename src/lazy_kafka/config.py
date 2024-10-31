"""Handle configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import tomllib

if TYPE_CHECKING:
    from _typeshed import SupportsRead


@dataclass
class KafkaConfiguration:
    bootstrap_server: str = "localhost:9092"


@dataclass
class ConnectConfiguration:
    host: str = "http://localhost:8083/"


@dataclass
class RegistryConfiguration:
    host: str = "http://localhost:8081/"


# TODO: @from_file(Path.home() / ".lazy-kafka.toml")
@dataclass(frozen=True)
class Configuration:
    """Lazy-kafka configuration."""

    kafka: KafkaConfiguration = field(default_factory=KafkaConfiguration)
    registry: RegistryConfiguration = field(default_factory=RegistryConfiguration)
    connect: ConnectConfiguration = field(default_factory=ConnectConfiguration)
    request_time_out: int = 1000

    @classmethod
    def from_file(
            cls, file_path: Path, file_reader: Callable[[SupportsRead], Any], **kwargs: Any
    ):
        with open(file_path, **kwargs) as _f:
            config = file_reader(_f)
        return cls(**config)

    @classmethod
    def from_toml(cls, file_path: Path):
        return cls.from_file(file_path, tomllib.load, mode="rb")

    @classmethod
    def from_json(cls, file_path: Path):
        return cls.from_file(file_path, json.load)


if __name__ == "__main__":
    from rich.pretty import pprint

    _p = Path(__file__).parent / "default_config.toml"
    pprint(Configuration.from_toml(_p))

