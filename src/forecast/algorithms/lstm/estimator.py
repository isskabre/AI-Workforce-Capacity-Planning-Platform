"""
AI Workforce Capacity Planning Platform
Implementation 12 - Enterprise Forecast Algorithm Library

Module:
    src.forecast.algorithms.lstm.estimator

Description:
    Implements the enterprise PyTorch LSTM regression estimator.

    The estimator supports deterministic sequence-model training, batch
    prediction, CPU/GPU device resolution, feature and target scaling,
    serialization, persistence, restoration, validation, and lifecycle
    management through the EnterpriseEstimator contract.

Architecture:
    Enterprise Forecast Modeling Framework

Version:
    2.4.0
"""

from __future__ import annotations

import base64
import io
import math
import random
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Any, Self

import numpy as np

from src.forecast.algorithms.base.estimator import EnterpriseEstimator
from src.forecast.algorithms.base.serializer import EnterpriseSerializer


def _require_torch():
    """
    Import and return PyTorch components.

    Raises:
        RuntimeError:
            If PyTorch is unavailable in the active runtime.
    """
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is required for the LSTM estimator but is not "
            "installed in the active Databricks runtime."
        ) from exc

    return torch, nn, DataLoader, TensorDataset


class _LSTMRegressorNetwork:
    """
    Lazy wrapper around the concrete PyTorch neural-network implementation.

    This wrapper prevents importing PyTorch when the module is imported.
    """

    @staticmethod
    def build(
        *,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        dropout: float,
        output_size: int = 1,
    ):
        torch, nn, _, _ = _require_torch()

        class LSTMRegressor(nn.Module):
            def __init__(self) -> None:
                super().__init__()

                effective_dropout = (
                    dropout
                    if num_layers > 1
                    else 0.0
                )

                self.lstm = nn.LSTM(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    batch_first=True,
                    dropout=effective_dropout,
                )

                self.output_layer = nn.Linear(
                    hidden_size,
                    output_size,
                )

            def forward(self, inputs):
                sequence_output, _ = self.lstm(inputs)

                final_hidden_state = sequence_output[:, -1, :]

                return self.output_layer(
                    final_hidden_state
                ).squeeze(-1)

        return LSTMRegressor()


class LSTMEstimator(EnterpriseEstimator):
    """
    Enterprise LSTM regression estimator implemented with PyTorch.

    Expected feature shape:

        (records, sequence_length, feature_count)

    A two-dimensional matrix is also accepted and is interpreted as:

        (records, 1, feature_count)

    The target must contain one numeric value per input sequence.
    """

    ESTIMATOR_NAME = "lstm_estimator"
    FRAMEWORK = "pytorch"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        hidden_size: int = 32,
        num_layers: int = 1,
        dropout: float = 0.0,
        learning_rate: float = 0.001,
        epochs: int = 20,
        batch_size: int = 32,
        weight_decay: float = 0.0,
        gradient_clip_norm: float | None = 1.0,
        random_state: int = 42,
        device: str = "auto",
        scale_features: bool = True,
        scale_target: bool = True,
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        self._validate_hyperparameters(
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            learning_rate=learning_rate,
            epochs=epochs,
            batch_size=batch_size,
            weight_decay=weight_decay,
            gradient_clip_norm=gradient_clip_norm,
            random_state=random_state,
            device=device,
            scale_features=scale_features,
            scale_target=scale_target,
        )

        resolved_parameters = {
            **dict(parameters or {}),
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "dropout": dropout,
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,
            "weight_decay": weight_decay,
            "gradient_clip_norm": gradient_clip_norm,
            "random_state": random_state,
            "device": device,
            "scale_features": scale_features,
            "scale_target": scale_target,
        }

        super().__init__(
            estimator_name=self.ESTIMATOR_NAME,
            framework=self.FRAMEWORK,
            version=self.VERSION,
            parameters=resolved_parameters,
        )

        self._hidden_size = hidden_size
        self._num_layers = num_layers
        self._dropout = dropout
        self._learning_rate = learning_rate
        self._epochs = epochs
        self._batch_size = batch_size
        self._weight_decay = weight_decay
        self._gradient_clip_norm = gradient_clip_norm
        self._random_state = random_state
        self._requested_device = device
        self._scale_features = scale_features
        self._scale_target = scale_target

        self._model: Any = None
        self._input_size: int | None = None
        self._sequence_length: int | None = None
        self._resolved_device: str | None = None

        self._feature_mean: tuple[float, ...] = ()
        self._feature_std: tuple[float, ...] = ()
        self._target_mean: float = 0.0
        self._target_std: float = 1.0

        self._training_loss_history: tuple[float, ...] = ()

    # ------------------------------------------------------------------
    # Configuration and learned state
    # ------------------------------------------------------------------

    @property
    def hidden_size(self) -> int:
        return self._hidden_size

    @property
    def num_layers(self) -> int:
        return self._num_layers

    @property
    def dropout(self) -> float:
        return self._dropout

    @property
    def learning_rate(self) -> float:
        return self._learning_rate

    @property
    def epochs(self) -> int:
        return self._epochs

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def weight_decay(self) -> float:
        return self._weight_decay

    @property
    def gradient_clip_norm(self) -> float | None:
        return self._gradient_clip_norm

    @property
    def random_state(self) -> int:
        return self._random_state

    @property
    def requested_device(self) -> str:
        return self._requested_device

    @property
    def resolved_device(self) -> str | None:
        return self._resolved_device

    @property
    def scale_features(self) -> bool:
        return self._scale_features

    @property
    def scale_target(self) -> bool:
        return self._scale_target

    @property
    def model(self) -> Any:
        return self._model

    @property
    def input_size(self) -> int | None:
        return self._input_size

    @property
    def sequence_length(self) -> int | None:
        return self._sequence_length

    @property
    def feature_mean(self) -> tuple[float, ...]:
        return self._feature_mean

    @property
    def feature_std(self) -> tuple[float, ...]:
        return self._feature_std

    @property
    def target_mean(self) -> float:
        return self._target_mean

    @property
    def target_std(self) -> float:
        return self._target_std

    @property
    def training_loss_history(self) -> tuple[float, ...]:
        return self._training_loss_history

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(
        self,
        features: Any,
        target: Any,
    ) -> Self:
        """
        Train the LSTM regression estimator.

        Args:
            features:
                Numeric feature tensor with shape
                ``(records, sequence_length, feature_count)``.
            target:
                One numeric target per sequence.

        Returns:
            This fitted estimator.
        """
        torch, nn, DataLoader, TensorDataset = _require_torch()

        feature_tensor = self._to_feature_tensor(features)
        target_vector = self._to_target_vector(target)

        record_count, sequence_length, input_size = (
            feature_tensor.shape
        )

        if record_count != target_vector.shape[0]:
            raise ValueError(
                "Feature and target record counts must match. "
                f"Received {record_count} feature records and "
                f"{target_vector.shape[0]} target records."
            )

        if record_count < 2:
            raise ValueError(
                "LSTM requires at least two training records."
            )

        self._set_deterministic_seed(torch)

        self._input_size = int(input_size)
        self._sequence_length = int(sequence_length)
        self._resolved_device = self._resolve_device(torch)

        scaled_features = self._fit_transform_features(
            feature_tensor
        )
        scaled_target = self._fit_transform_target(
            target_vector
        )

        torch_features = torch.tensor(
            scaled_features,
            dtype=torch.float32,
        )
        torch_target = torch.tensor(
            scaled_target,
            dtype=torch.float32,
        )

        dataset = TensorDataset(
            torch_features,
            torch_target,
        )

        generator = torch.Generator()
        generator.manual_seed(self.random_state)

        data_loader = DataLoader(
            dataset,
            batch_size=min(
                self.batch_size,
                record_count,
            ),
            shuffle=True,
            generator=generator,
        )

        model = _LSTMRegressorNetwork.build(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
        )

        model = model.to(self._resolved_device)

        loss_function = nn.MSELoss()

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )

        epoch_losses: list[float] = []

        model.train()

        for _ in range(self.epochs):
            total_loss = 0.0
            total_records = 0

            for batch_features, batch_target in data_loader:
                batch_features = batch_features.to(
                    self._resolved_device
                )
                batch_target = batch_target.to(
                    self._resolved_device
                )

                optimizer.zero_grad()

                predictions = model(batch_features)

                loss = loss_function(
                    predictions,
                    batch_target,
                )

                loss.backward()

                if self.gradient_clip_norm is not None:
                    torch.nn.utils.clip_grad_norm_(
                        model.parameters(),
                        max_norm=self.gradient_clip_norm,
                    )

                optimizer.step()

                batch_record_count = (
                    batch_features.shape[0]
                )

                total_loss += (
                    float(loss.detach().cpu().item())
                    * batch_record_count
                )
                total_records += batch_record_count

            epoch_losses.append(
                total_loss / total_records
            )

        self._model = model
        self._training_loss_history = tuple(
            epoch_losses
        )

        # Calculate training predictions directly because the estimator
        # has not yet transitioned to the fitted lifecycle state.
        model.eval()

        with torch.no_grad():
            training_feature_tensor = torch.tensor(
                scaled_features,
                dtype=torch.float32,
                device=self.resolved_device,
            )

            scaled_training_predictions = model(
                training_feature_tensor
            ).detach().cpu().numpy()

        training_predictions = self._inverse_transform_target(
            scaled_training_predictions
        )

        residuals = (
            target_vector
            - np.asarray(
                training_predictions,
                dtype=float,
            )
        )

        training_mse = float(
            np.mean(np.square(residuals))
        )
        training_rmse = float(
            np.sqrt(training_mse)
        )
        training_mae = float(
            np.mean(np.abs(residuals))
        )

        self.mark_fitted(
            training_metadata={
                "training_records": record_count,
                "sequence_length": sequence_length,
                "feature_count": input_size,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "dropout": self.dropout,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "weight_decay": self.weight_decay,
                "resolved_device": self.resolved_device,
                "final_training_loss": (
                    self.training_loss_history[-1]
                ),
                "training_mae": training_mae,
                "training_mse": training_mse,
                "training_rmse": training_rmse,
            }
        )

        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(
        self,
        features: Any,
    ) -> tuple[float, ...]:
        """Generate LSTM regression predictions."""
        torch, _, _, _ = _require_torch()

        model = self._require_fitted_model()

        feature_tensor = self._to_feature_tensor(features)

        self._validate_prediction_shape(
            feature_tensor
        )

        scaled_features = self._transform_features(
            feature_tensor
        )

        torch_features = torch.tensor(
            scaled_features,
            dtype=torch.float32,
            device=self.resolved_device,
        )

        model.eval()

        with torch.no_grad():
            scaled_predictions = model(
                torch_features
            ).detach().cpu().numpy()

        predictions = self._inverse_transform_target(
            scaled_predictions
        )

        return tuple(
            float(value)
            for value in predictions
        )

    # ------------------------------------------------------------------
    # Serialization and persistence
    # ------------------------------------------------------------------

    def serialize(self) -> Mapping[str, Any]:
        """
        Return serialization-safe estimator state.

        The PyTorch ``state_dict`` is encoded as Base64.
        """
        torch, _, _, _ = _require_torch()

        model_blob = None

        if self._model is not None:
            buffer = io.BytesIO()

            torch.save(
                self._model.state_dict(),
                buffer,
            )

            model_blob = base64.b64encode(
                buffer.getvalue()
            ).decode("ascii")

        return {
            "schema_version": "1.0",
            "estimator_name": self.estimator_name,
            "framework": self.framework,
            "version": self.version,
            "parameters": dict(self.parameters),
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout": self.dropout,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "weight_decay": self.weight_decay,
            "gradient_clip_norm": self.gradient_clip_norm,
            "random_state": self.random_state,
            "requested_device": self.requested_device,
            "resolved_device": self.resolved_device,
            "scale_features": self.scale_features,
            "scale_target": self.scale_target,
            "initialized": self.initialized,
            "fitted": self.fitted,
            "feature_names": list(self.feature_names),
            "target_name": self.target_name,
            "training_metadata": dict(
                self.training_metadata
            ),
            "input_size": self.input_size,
            "sequence_length": self.sequence_length,
            "feature_mean": list(self.feature_mean),
            "feature_std": list(self.feature_std),
            "target_mean": self.target_mean,
            "target_std": self.target_std,
            "training_loss_history": list(
                self.training_loss_history
            ),
            "model_blob": model_blob,
        }

    @classmethod
    def deserialize(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        """Reconstruct an LSTM estimator from serialized state."""
        torch, _, _, _ = _require_torch()

        estimator = cls(
            hidden_size=int(
                payload.get("hidden_size", 32)
            ),
            num_layers=int(
                payload.get("num_layers", 1)
            ),
            dropout=float(
                payload.get("dropout", 0.0)
            ),
            learning_rate=float(
                payload.get("learning_rate", 0.001)
            ),
            epochs=int(
                payload.get("epochs", 20)
            ),
            batch_size=int(
                payload.get("batch_size", 32)
            ),
            weight_decay=float(
                payload.get("weight_decay", 0.0)
            ),
            gradient_clip_norm=payload.get(
                "gradient_clip_norm",
                1.0,
            ),
            random_state=int(
                payload.get("random_state", 42)
            ),
            device=str(
                payload.get(
                    "requested_device",
                    "auto",
                )
            ),
            scale_features=bool(
                payload.get("scale_features", True)
            ),
            scale_target=bool(
                payload.get("scale_target", True)
            ),
            parameters=payload.get("parameters"),
        )

        estimator._initialized = bool(
            payload.get("initialized", False)
        )
        estimator._fitted = bool(
            payload.get("fitted", False)
        )
        estimator._feature_names = tuple(
            payload.get("feature_names", ())
        )
        estimator._target_name = payload.get(
            "target_name"
        )
        estimator._training_metadata = dict(
            payload.get("training_metadata", {})
        )

        input_size = payload.get("input_size")
        sequence_length = payload.get(
            "sequence_length"
        )

        estimator._input_size = (
            int(input_size)
            if input_size is not None
            else None
        )
        estimator._sequence_length = (
            int(sequence_length)
            if sequence_length is not None
            else None
        )

        estimator._resolved_device = (
            estimator._resolve_device(torch)
        )

        estimator._feature_mean = tuple(
            float(value)
            for value in payload.get(
                "feature_mean",
                (),
            )
        )
        estimator._feature_std = tuple(
            float(value)
            for value in payload.get(
                "feature_std",
                (),
            )
        )
        estimator._target_mean = float(
            payload.get("target_mean", 0.0)
        )
        estimator._target_std = float(
            payload.get("target_std", 1.0)
        )
        estimator._training_loss_history = tuple(
            float(value)
            for value in payload.get(
                "training_loss_history",
                (),
            )
        )

        model_blob = payload.get("model_blob")

        if model_blob is not None:
            if estimator.input_size is None:
                raise ValueError(
                    "Serialized LSTM estimator is missing input_size."
                )

            model = _LSTMRegressorNetwork.build(
                input_size=estimator.input_size,
                hidden_size=estimator.hidden_size,
                num_layers=estimator.num_layers,
                dropout=estimator.dropout,
            )

            state_bytes = base64.b64decode(
                model_blob.encode("ascii")
            )

            state_buffer = io.BytesIO(
                state_bytes
            )

            state_dict = torch.load(
                state_buffer,
                map_location=estimator.resolved_device,
            )

            model.load_state_dict(
                state_dict
            )

            estimator._model = model.to(
                estimator.resolved_device
            )

        if estimator._fitted and estimator._model is None:
            raise ValueError(
                "A fitted LSTM estimator must contain serialized "
                "model state."
            )

        return estimator

    def save(
        self,
        destination: str | PathLike[str],
    ) -> None:
        """Persist estimator state as JSON."""
        EnterpriseSerializer.save_json(
            self.serialize(),
            Path(destination),
        )

    @classmethod
    def load(
        cls,
        source: str | PathLike[str],
    ) -> Self:
        """Load estimator state from JSON."""
        payload = EnterpriseSerializer.load_json(
            Path(source)
        )

        return cls.deserialize(payload)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset lifecycle and all learned neural-network state."""
        super().reset()

        self._model = None
        self._input_size = None
        self._sequence_length = None
        self._resolved_device = None

        self._feature_mean = ()
        self._feature_std = ()
        self._target_mean = 0.0
        self._target_std = 1.0

        self._training_loss_history = ()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_fitted_model(self):
        if not self.fitted or self._model is None:
            raise RuntimeError(
                "LSTM estimator must be fitted before prediction."
            )

        return self._model

    def _validate_prediction_shape(
        self,
        features: np.ndarray,
    ) -> None:
        if self.input_size is None:
            raise RuntimeError(
                "LSTM fitted input size is unavailable."
            )

        if self.sequence_length is None:
            raise RuntimeError(
                "LSTM fitted sequence length is unavailable."
            )

        if features.shape[1] != self.sequence_length:
            raise ValueError(
                "Prediction sequence length does not match the fitted "
                "sequence length. "
                f"Received {features.shape[1]}; "
                f"expected {self.sequence_length}."
            )

        if features.shape[2] != self.input_size:
            raise ValueError(
                "Prediction feature count does not match the fitted "
                "feature count. "
                f"Received {features.shape[2]}; "
                f"expected {self.input_size}."
            )

    def _set_deterministic_seed(self, torch) -> None:
        random.seed(self.random_state)
        np.random.seed(self.random_state)
        torch.manual_seed(self.random_state)

        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(
                self.random_state
            )

        if hasattr(
            torch.backends,
            "cudnn",
        ):
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    def _resolve_device(self, torch) -> str:
        requested = self.requested_device.lower()

        if requested == "auto":
            return (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        if requested == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA was requested for the LSTM estimator, but "
                    "no CUDA device is available."
                )

            return "cuda"

        return "cpu"

    def _fit_transform_features(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        if not self.scale_features:
            self._feature_mean = tuple(
                0.0
                for _ in range(features.shape[2])
            )
            self._feature_std = tuple(
                1.0
                for _ in range(features.shape[2])
            )

            return features.copy()

        flattened = features.reshape(
            -1,
            features.shape[2],
        )

        means = np.mean(
            flattened,
            axis=0,
        )
        standard_deviations = np.std(
            flattened,
            axis=0,
        )

        standard_deviations = np.where(
            standard_deviations == 0.0,
            1.0,
            standard_deviations,
        )

        self._feature_mean = tuple(
            float(value)
            for value in means
        )
        self._feature_std = tuple(
            float(value)
            for value in standard_deviations
        )

        return (
            features
            - means.reshape(1, 1, -1)
        ) / standard_deviations.reshape(
            1,
            1,
            -1,
        )

    def _transform_features(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        means = np.asarray(
            self.feature_mean,
            dtype=float,
        ).reshape(1, 1, -1)

        standard_deviations = np.asarray(
            self.feature_std,
            dtype=float,
        ).reshape(1, 1, -1)

        return (
            features - means
        ) / standard_deviations

    def _fit_transform_target(
        self,
        target: np.ndarray,
    ) -> np.ndarray:
        if not self.scale_target:
            self._target_mean = 0.0
            self._target_std = 1.0

            return target.copy()

        self._target_mean = float(
            np.mean(target)
        )
        target_std = float(
            np.std(target)
        )

        self._target_std = (
            target_std
            if target_std != 0.0
            else 1.0
        )

        return (
            target - self.target_mean
        ) / self.target_std

    def _inverse_transform_target(
        self,
        target: np.ndarray,
    ) -> np.ndarray:
        return (
            target * self.target_std
            + self.target_mean
        )

    @staticmethod
    def _to_feature_tensor(
        features: Any,
    ) -> np.ndarray:
        if features is None:
            raise ValueError(
                "features must not be None."
            )

        try:
            tensor = np.asarray(
                features,
                dtype=float,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "features must contain numeric values."
            ) from exc

        if tensor.ndim == 2:
            tensor = tensor[:, np.newaxis, :]

        if tensor.ndim != 3:
            raise ValueError(
                "LSTM features must be a three-dimensional tensor "
                "with shape (records, sequence_length, feature_count)."
            )

        if tensor.shape[0] == 0:
            raise ValueError(
                "features must contain at least one record."
            )

        if tensor.shape[1] == 0:
            raise ValueError(
                "features must contain at least one sequence step."
            )

        if tensor.shape[2] == 0:
            raise ValueError(
                "features must contain at least one feature."
            )

        if not np.isfinite(tensor).all():
            raise ValueError(
                "features must contain only finite values."
            )

        return tensor

    @staticmethod
    def _to_target_vector(
        target: Any,
    ) -> np.ndarray:
        if target is None:
            raise ValueError(
                "target must not be None."
            )

        try:
            vector = np.asarray(
                target,
                dtype=float,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "target must contain numeric values."
            ) from exc

        if vector.ndim == 2 and vector.shape[1] == 1:
            vector = vector.reshape(-1)

        if vector.ndim != 1:
            raise ValueError(
                "target must be one-dimensional."
            )

        if vector.size == 0:
            raise ValueError(
                "target must contain at least one value."
            )

        if not np.isfinite(vector).all():
            raise ValueError(
                "target must contain only finite values."
            )

        return vector

    @staticmethod
    def _validate_hyperparameters(
        *,
        hidden_size: int,
        num_layers: int,
        dropout: float,
        learning_rate: float,
        epochs: int,
        batch_size: int,
        weight_decay: float,
        gradient_clip_norm: float | None,
        random_state: int,
        device: str,
        scale_features: bool,
        scale_target: bool,
    ) -> None:
        integer_fields = {
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "epochs": epochs,
            "batch_size": batch_size,
        }

        for field_name, value in integer_fields.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value <= 0
            ):
                raise ValueError(
                    f"{field_name} must be a positive integer."
                )

        if not 0.0 <= dropout < 1.0:
            raise ValueError(
                "dropout must be in the interval [0, 1)."
            )

        if learning_rate <= 0.0:
            raise ValueError(
                "learning_rate must be greater than zero."
            )

        if weight_decay < 0.0:
            raise ValueError(
                "weight_decay must be greater than or equal to zero."
            )

        if (
            gradient_clip_norm is not None
            and gradient_clip_norm <= 0.0
        ):
            raise ValueError(
                "gradient_clip_norm must be None or greater than zero."
            )

        if (
            isinstance(random_state, bool)
            or not isinstance(random_state, int)
        ):
            raise ValueError(
                "random_state must be an integer."
            )

        if device.lower() not in {
            "auto",
            "cpu",
            "cuda",
        }:
            raise ValueError(
                "device must be 'auto', 'cpu', or 'cuda'."
            )

        if not isinstance(scale_features, bool):
            raise ValueError(
                "scale_features must be a boolean."
            )

        if not isinstance(scale_target, bool):
            raise ValueError(
                "scale_target must be a boolean."
            )


__all__ = [
    "LSTMEstimator",
]