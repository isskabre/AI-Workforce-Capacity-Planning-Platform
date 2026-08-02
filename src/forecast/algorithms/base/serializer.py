"""
AI Workforce Capacity Planning Platform
Implementation 11 - Enterprise Forecast Modeling Framework

Module:
    forecast.algorithms.base.serializer

Description:
    Enterprise serialization framework used by forecasting models and
    estimators.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class EnterpriseSerializer(ABC):
    """
    Enterprise serialization helper.

    Provides JSON serialization, persistence and checksum generation.
    """

    # ==========================================================
    # JSON
    # ==========================================================

    @staticmethod
    def dumps(
        payload: Mapping[str, Any],
        *,
        indent: int = 4,
    ) -> str:
        return json.dumps(
            payload,
            indent=indent,
            sort_keys=True,
            default=str,
        )

    @staticmethod
    def loads(
        payload: str,
    ) -> dict[str, Any]:
        return json.loads(payload)

    # ==========================================================
    # Files
    # ==========================================================

    @classmethod
    def save_json(
        cls,
        payload: Mapping[str, Any],
        destination: str | Path,
    ) -> None:

        destination = Path(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_text(
            cls.dumps(payload),
            encoding="utf-8",
        )

    @classmethod
    def load_json(
        cls,
        source: str | Path,
    ) -> dict[str, Any]:

        source = Path(source)

        return cls.loads(
            source.read_text(
                encoding="utf-8",
            )
        )

    # ==========================================================
    # Checksum
    # ==========================================================

    @classmethod
    def checksum(
        cls,
        payload: Mapping[str, Any],
    ) -> str:

        encoded = cls.dumps(
            payload,
            indent=None,
        ).encode("utf-8")

        return hashlib.sha256(
            encoded
        ).hexdigest()

    # ==========================================================
    # Metadata
    # ==========================================================

    @classmethod
    def package(
        cls,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:

        return {
            "checksum": cls.checksum(payload),
            "payload": dict(payload),
        }


__all__ = [
    "EnterpriseSerializer",
]