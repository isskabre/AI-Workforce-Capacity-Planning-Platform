"""
AI Workforce Capacity Planning Platform
Implementation 14 - Enterprise Inference Framework

Module:
    forecast.inference.batch_predictor

Description:
    Provides deterministic orchestration for executing multiple enterprise
    forecast prediction requests through EnterpriseForecastPredictor.

Architecture:
    Enterprise Inference Framework

Version:
    2.7.0
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from forecast.inference.predictor import (
    EnterpriseForecastPredictor,
)
from forecast.modeling.contexts import (
    ForecastPredictionContext,
)
from forecast.modeling.contracts import (
    BaseForecastModel,
)
from forecast.modeling.exceptions import (
    ForecastInferenceError,
)
from forecast.modeling.results import (
    ForecastPredictionResult,
)


@dataclass(frozen=True, slots=True)
class ForecastBatchPredictionRequest:
    """
    Immutable request for one prediction within a batch execution.

    Attributes:
        request_id:
            Stable request identifier unique within the batch.

        model:
            Initialized and trained enterprise forecasting model.

        context:
            Immutable prediction execution context.

        metadata:
            Optional request-level metadata.
    """

    request_id: str
    model: BaseForecastModel
    context: ForecastPredictionContext
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str):
            raise ForecastInferenceError(
                "Batch prediction request_id must be a string.",
                context={
                    "received_type": type(
                        self.request_id
                    ).__name__,
                },
            )

        normalized_request_id = self.request_id.strip()

        if not normalized_request_id:
            raise ForecastInferenceError(
                "Batch prediction request_id must not be empty."
            )

        if not isinstance(self.metadata, Mapping):
            raise ForecastInferenceError(
                "Batch prediction request metadata must be a mapping.",
                context={
                    "request_id": normalized_request_id,
                    "received_type": type(
                        self.metadata
                    ).__name__,
                },
            )

        object.__setattr__(
            self,
            "request_id",
            normalized_request_id,
        )
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )


@dataclass(frozen=True, slots=True)
class ForecastBatchPredictionItem:
    """
    Immutable outcome for one request in a batch prediction execution.

    Exactly one of ``prediction`` or ``error`` is populated.

    Attributes:
        request_id:
            Request identifier supplied by the caller.

        model_name:
            Stable enterprise model name.

        model_version:
            Model implementation version.

        succeeded:
            Whether the individual request completed successfully.

        prediction:
            Standard prediction result when successful.

        error:
            Serialized enterprise error when unsuccessful.

        metadata:
            Copied request-level metadata.
    """

    request_id: str
    model_name: str
    model_version: str
    succeeded: bool
    prediction: ForecastPredictionResult | None = None
    error: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str):
            raise ForecastInferenceError(
                "Batch item request_id must be a string."
            )

        if not self.request_id.strip():
            raise ForecastInferenceError(
                "Batch item request_id must not be empty."
            )

        if not isinstance(self.model_name, str):
            raise ForecastInferenceError(
                "Batch item model_name must be a string."
            )

        if not self.model_name.strip():
            raise ForecastInferenceError(
                "Batch item model_name must not be empty."
            )

        if not isinstance(self.model_version, str):
            raise ForecastInferenceError(
                "Batch item model_version must be a string."
            )

        if not self.model_version.strip():
            raise ForecastInferenceError(
                "Batch item model_version must not be empty."
            )

        if not isinstance(self.succeeded, bool):
            raise ForecastInferenceError(
                "Batch item succeeded must be a boolean."
            )

        if not isinstance(self.metadata, Mapping):
            raise ForecastInferenceError(
                "Batch item metadata must be a mapping."
            )

        if self.succeeded:
            if not isinstance(
                self.prediction,
                ForecastPredictionResult,
            ):
                raise ForecastInferenceError(
                    "Successful batch items must contain a "
                    "ForecastPredictionResult.",
                    context={
                        "request_id": self.request_id,
                    },
                )

            if self.error is not None:
                raise ForecastInferenceError(
                    "Successful batch items cannot contain error details.",
                    context={
                        "request_id": self.request_id,
                    },
                )

        else:
            if self.prediction is not None:
                raise ForecastInferenceError(
                    "Failed batch items cannot contain a prediction result.",
                    context={
                        "request_id": self.request_id,
                    },
                )

            if not isinstance(self.error, Mapping):
                raise ForecastInferenceError(
                    "Failed batch items must contain error details.",
                    context={
                        "request_id": self.request_id,
                    },
                )

        object.__setattr__(
            self,
            "request_id",
            self.request_id.strip(),
        )
        object.__setattr__(
            self,
            "model_name",
            self.model_name.strip(),
        )
        object.__setattr__(
            self,
            "model_version",
            self.model_version.strip(),
        )
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

        if self.error is not None:
            object.__setattr__(
                self,
                "error",
                dict(self.error),
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe batch item."""
        return {
            "request_id": self.request_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "succeeded": self.succeeded,
            "prediction": (
                self.prediction.to_dict()
                if self.prediction is not None
                else None
            ),
            "error": (
                dict(self.error)
                if self.error is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ForecastBatchPredictionResult:
    """
    Immutable aggregate result for one batch prediction execution.

    Attributes:
        items:
            Ordered request outcomes matching the input request order.

        batch_id:
            Unique batch execution identifier.

        started_at:
            UTC timestamp when execution began.

        completed_at:
            UTC timestamp when execution completed.

        fail_fast:
            Whether execution was configured to stop on the first failure.

        metadata:
            Optional batch-level metadata.
    """

    items: tuple[ForecastBatchPredictionItem, ...]
    batch_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    fail_fast: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise ForecastInferenceError(
                "Batch prediction items must be stored as a tuple."
            )

        if not self.items:
            raise ForecastInferenceError(
                "Batch prediction result must contain at least one item."
            )

        if any(
            not isinstance(
                item,
                ForecastBatchPredictionItem,
            )
            for item in self.items
        ):
            raise ForecastInferenceError(
                "Every batch result item must be a "
                "ForecastBatchPredictionItem."
            )

        if not isinstance(self.batch_id, str):
            raise ForecastInferenceError(
                "Batch prediction batch_id must be a string."
            )

        if not self.batch_id.strip():
            raise ForecastInferenceError(
                "Batch prediction batch_id must not be empty."
            )

        self._validate_datetime(
            self.started_at,
            field_name="started_at",
        )
        self._validate_datetime(
            self.completed_at,
            field_name="completed_at",
        )

        if self.completed_at < self.started_at:
            raise ForecastInferenceError(
                "Batch prediction completed_at cannot precede started_at."
            )

        if not isinstance(self.fail_fast, bool):
            raise ForecastInferenceError(
                "Batch prediction fail_fast must be a boolean."
            )

        if not isinstance(self.metadata, Mapping):
            raise ForecastInferenceError(
                "Batch prediction metadata must be a mapping."
            )

        request_ids = tuple(
            item.request_id
            for item in self.items
        )

        if len(set(request_ids)) != len(request_ids):
            raise ForecastInferenceError(
                "Batch prediction result contains duplicate request IDs."
            )

        object.__setattr__(
            self,
            "batch_id",
            self.batch_id.strip(),
        )
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def total_requests(self) -> int:
        """Return the number of processed requests."""
        return len(self.items)

    @property
    def successful_requests(self) -> int:
        """Return the number of successful requests."""
        return sum(
            item.succeeded
            for item in self.items
        )

    @property
    def failed_requests(self) -> int:
        """Return the number of unsuccessful requests."""
        return (
            self.total_requests
            - self.successful_requests
        )

    @property
    def succeeded(self) -> bool:
        """Return whether every request succeeded."""
        return self.failed_requests == 0

    @property
    def predictions(
        self,
    ) -> tuple[ForecastPredictionResult, ...]:
        """Return successful prediction results in request order."""
        return tuple(
            item.prediction
            for item in self.items
            if item.prediction is not None
        )

    @property
    def failures(
        self,
    ) -> tuple[ForecastBatchPredictionItem, ...]:
        """Return unsuccessful batch items in request order."""
        return tuple(
            item
            for item in self.items
            if not item.succeeded
        )

    def get_item(
        self,
        request_id: str,
    ) -> ForecastBatchPredictionItem:
        """
        Return one batch item by request identifier.

        Raises:
            KeyError:
                If the request identifier is not present.
        """
        if not isinstance(request_id, str):
            raise TypeError(
                "request_id must be a string."
            )

        normalized_request_id = request_id.strip()

        if not normalized_request_id:
            raise ValueError(
                "request_id must not be empty."
            )

        for item in self.items:
            if item.request_id == normalized_request_id:
                return item

        raise KeyError(
            f"Batch request was not found: {normalized_request_id}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-safe batch result."""
        return {
            "batch_id": self.batch_id,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "succeeded": self.succeeded,
            "fail_fast": self.fail_fast,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "metadata": dict(self.metadata),
            "items": [
                item.to_dict()
                for item in self.items
            ],
        }

    @staticmethod
    def _validate_datetime(
        value: Any,
        *,
        field_name: str,
    ) -> None:
        """Validate one timezone-aware datetime."""
        if not isinstance(value, datetime):
            raise ForecastInferenceError(
                f"Batch prediction {field_name} must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ForecastInferenceError(
                f"Batch prediction {field_name} must be timezone-aware."
            )


class EnterpriseForecastBatchPredictor:
    """
    Orchestrate multiple enterprise forecast prediction requests.

    Single-request model validation, context validation, execution, and result
    validation are delegated exclusively to ``EnterpriseForecastPredictor``.

    Batch orchestration owns:

    - request collection validation;
    - duplicate request-ID detection;
    - deterministic execution order;
    - fail-fast or continue-on-error behavior;
    - aggregate batch result construction.

    The batch predictor does not duplicate single-request inference logic.
    """

    def __init__(
        self,
        *,
        predictor: EnterpriseForecastPredictor | None = None,
    ) -> None:
        """
        Initialize the batch predictor.

        Args:
            predictor:
                Optional single-request predictor dependency. A default
                EnterpriseForecastPredictor is created when omitted.
        """
        if predictor is not None and not isinstance(
            predictor,
            EnterpriseForecastPredictor,
        ):
            raise ForecastInferenceError(
                "predictor must be an EnterpriseForecastPredictor.",
                context={
                    "received_type": type(
                        predictor
                    ).__name__,
                },
            )

        self._predictor = (
            predictor
            if predictor is not None
            else EnterpriseForecastPredictor()
        )

    def predict(
        self,
        *,
        requests: Sequence[ForecastBatchPredictionRequest],
        fail_fast: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> ForecastBatchPredictionResult:
        """
        Execute an ordered batch of enterprise prediction requests.

        Args:
            requests:
                Ordered prediction requests.

            fail_fast:
                When ``True``, raise immediately after the first failed
                request. When ``False``, capture individual failures and
                continue processing remaining requests.

            metadata:
                Optional batch-level metadata.

        Returns:
            Immutable aggregate batch prediction result.

        Raises:
            ForecastInferenceError:
                If batch validation fails or a request fails while fail-fast
                mode is enabled.
        """
        validated_requests = self._validate_requests(
            requests
        )
        validated_fail_fast = self._validate_fail_fast(
            fail_fast
        )
        validated_metadata = self._validate_metadata(
            metadata
        )

        started_at = datetime.now(timezone.utc)
        items: list[ForecastBatchPredictionItem] = []

        for index, request in enumerate(
            validated_requests
        ):
            try:
                prediction = self._predictor.predict(
                    model=request.model,
                    context=request.context,
                )

                items.append(
                    ForecastBatchPredictionItem(
                        request_id=request.request_id,
                        model_name=prediction.model_name,
                        model_version=prediction.model_version,
                        succeeded=True,
                        prediction=prediction,
                        metadata=request.metadata,
                    )
                )

            except ForecastInferenceError as exc:
                if validated_fail_fast:
                    raise ForecastInferenceError(
                        "Batch forecast inference failed.",
                        context={
                            "request_index": index,
                            "request_id": request.request_id,
                            "model_name": self._safe_model_name(
                                request.model
                            ),
                            "model_version": self._safe_model_version(
                                request.model
                            ),
                            "completed_requests": len(items),
                            "total_requests": len(
                                validated_requests
                            ),
                            "fail_fast": True,
                        },
                        cause=exc,
                    ) from exc

                items.append(
                    ForecastBatchPredictionItem(
                        request_id=request.request_id,
                        model_name=self._safe_model_name(
                            request.model
                        ),
                        model_version=self._safe_model_version(
                            request.model
                        ),
                        succeeded=False,
                        error=exc.to_dict(),
                        metadata=request.metadata,
                    )
                )

        completed_at = datetime.now(timezone.utc)

        return ForecastBatchPredictionResult(
            items=tuple(items),
            started_at=started_at,
            completed_at=completed_at,
            fail_fast=validated_fail_fast,
            metadata=validated_metadata,
        )

    @staticmethod
    def _validate_requests(
        requests: Sequence[ForecastBatchPredictionRequest],
    ) -> tuple[ForecastBatchPredictionRequest, ...]:
        """Validate and materialize the ordered request collection."""
        if requests is None:
            raise ForecastInferenceError(
                "Batch prediction requests cannot be None."
            )

        if isinstance(
            requests,
            (str, bytes, bytearray, Mapping),
        ):
            raise ForecastInferenceError(
                "Batch prediction requests must be a sequence of "
                "ForecastBatchPredictionRequest objects."
            )

        try:
            materialized_requests = tuple(requests)
        except TypeError as exc:
            raise ForecastInferenceError(
                "Batch prediction requests must be iterable.",
                cause=exc,
            ) from exc

        if not materialized_requests:
            raise ForecastInferenceError(
                "At least one batch prediction request is required."
            )

        request_ids: set[str] = set()

        for index, request in enumerate(
            materialized_requests
        ):
            if not isinstance(
                request,
                ForecastBatchPredictionRequest,
            ):
                raise ForecastInferenceError(
                    "Every batch prediction request must be a "
                    "ForecastBatchPredictionRequest.",
                    context={
                        "index": index,
                        "received_type": type(
                            request
                        ).__name__,
                    },
                )

            normalized_request_id = (
                request.request_id.strip().lower()
            )

            if normalized_request_id in request_ids:
                raise ForecastInferenceError(
                    "Duplicate batch prediction request IDs are not allowed.",
                    context={
                        "request_id": request.request_id,
                        "index": index,
                    },
                )

            request_ids.add(normalized_request_id)

        return materialized_requests

    @staticmethod
    def _validate_fail_fast(
        fail_fast: bool,
    ) -> bool:
        """Validate batch failure behavior."""
        if not isinstance(fail_fast, bool):
            raise ForecastInferenceError(
                "fail_fast must be a boolean.",
                context={
                    "received_type": type(
                        fail_fast
                    ).__name__,
                },
            )

        return fail_fast

    @staticmethod
    def _validate_metadata(
        metadata: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        """Validate and copy optional batch metadata."""
        if metadata is None:
            return {}

        if not isinstance(metadata, Mapping):
            raise ForecastInferenceError(
                "Batch prediction metadata must be a mapping.",
                context={
                    "received_type": type(
                        metadata
                    ).__name__,
                },
            )

        return dict(metadata)

    @staticmethod
    def _safe_model_name(
        model: Any,
    ) -> str:
        """Return a safe model name for failed request reporting."""
        value = getattr(
            model,
            "model_name",
            None,
        )

        if isinstance(value, str) and value.strip():
            return value.strip()

        return "<unknown-model>"

    @staticmethod
    def _safe_model_version(
        model: Any,
    ) -> str:
        """Return a safe model version for failed request reporting."""
        value = getattr(
            model,
            "model_version",
            None,
        )

        if isinstance(value, str) and value.strip():
            return value.strip()

        return "<unknown-version>"


__all__ = [
    "EnterpriseForecastBatchPredictor",
    "ForecastBatchPredictionItem",
    "ForecastBatchPredictionRequest",
    "ForecastBatchPredictionResult",
]