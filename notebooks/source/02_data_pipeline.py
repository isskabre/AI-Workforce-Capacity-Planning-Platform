# Databricks notebook source
# MAGIC %md
# MAGIC # Data Foundation Pipeline
# MAGIC
# MAGIC ## Responsibility
# MAGIC
# MAGIC This notebook is the operational entry point for enterprise dataset acquisition.
# MAGIC
# MAGIC It currently:
# MAGIC
# MAGIC 1. imports shared project configuration,
# MAGIC 2. reads and validates the persistent dataset registry,
# MAGIC 3. selects enabled acquisition-ready datasets,
# MAGIC 4. downloads supported source datasets into temporary driver storage,
# MAGIC 5. validates the downloaded artifacts,
# MAGIC 6. persists source files unchanged into the S3 Landing/raw zone,
# MAGIC 7. validates the persistent Landing copy.
# MAGIC
# MAGIC Manifest generation and generalized provider dispatching will be added in the next sections.

# COMMAND ----------

# MAGIC %run ../00_project_setup/00_project_setup

# COMMAND ----------

# ============================================================
# Enterprise Data Platform
# Implementation 04
# Section 1 — Acquisition Runtime Configuration
# ============================================================

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import logging
import shutil
import uuid

# ------------------------------------------------------------
# Pipeline identity
# ------------------------------------------------------------

PIPELINE_NAME = "enterprise-dataset-acquisition"
PIPELINE_VERSION = "1.0.0"

# PROJECT_VERSION, ENVIRONMENT, and persistent S3 paths are
# imported from 00_project_setup and are not redefined here.

# ------------------------------------------------------------
# Required shared configuration
# ------------------------------------------------------------

_REQUIRED_CONFIGURATION = (
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "ENVIRONMENT",
    "PROJECT_ROOT",
    "LANDING_RAW_ROOT",
    "DATASET_REGISTRY_PATH",
    "MANIFEST_ROOT",
    "ACQUISITION_METADATA_PATH",
    "STORAGE_CONNECTION_OK",
)

missing_configuration = [
    name
    for name in _REQUIRED_CONFIGURATION
    if name not in globals()
]

if missing_configuration:
    raise RuntimeError(
        "Missing shared project configuration: "
        + ", ".join(missing_configuration)
    )

if STORAGE_CONNECTION_OK is not True:
    raise RuntimeError(
        "Persistent project storage is not available."
    )

# ------------------------------------------------------------
# Databricks Workspace staging area
# ------------------------------------------------------------

# Serverless compute does not allow dbutils.fs to copy files
# directly from arbitrary /tmp locations. Files are therefore
# downloaded into the current user's Workspace Files directory.

current_user_row = spark.sql(
    "SELECT current_user() AS current_user"
).first()

if current_user_row is None:
    raise RuntimeError(
        "Unable to resolve the current Databricks user."
    )

CURRENT_USER = current_user_row["current_user"]

if not CURRENT_USER:
    raise RuntimeError(
        "The current Databricks user is empty."
    )

WORKSPACE_PATH = Path(
    f"/Workspace/Users/{CURRENT_USER}/"
    "overtime_capacity_planning"
)

DOWNLOAD_PATH = WORKSPACE_PATH / "downloads"
MANIFEST_LOCAL_PATH = WORKSPACE_PATH / "manifests"

DOWNLOAD_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

MANIFEST_LOCAL_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

# Validate that the staging locations were created successfully.

if not DOWNLOAD_PATH.is_dir():
    raise RuntimeError(
        f"Unable to create download staging directory: "
        f"{DOWNLOAD_PATH}"
    )

if not MANIFEST_LOCAL_PATH.is_dir():
    raise RuntimeError(
        f"Unable to create manifest staging directory: "
        f"{MANIFEST_LOCAL_PATH}"
    )

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logger = logging.getLogger(PIPELINE_NAME)

if not logger.handlers:
    handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False

logger.info(
    "Acquisition runtime initialized | "
    "pipeline=%s | version=%s | environment=%s | "
    "workspace_path=%s",
    PIPELINE_NAME,
    PIPELINE_VERSION,
    ENVIRONMENT,
    WORKSPACE_PATH,
)

# COMMAND ----------

print("=" * 60)
print("Enterprise Dataset Acquisition")
print("=" * 60)

print(f"Project      : {PROJECT_NAME}")
print(f"Pipeline     : {PIPELINE_NAME}")
print(f"Version      : {PIPELINE_VERSION}")
print(f"Environment  : {ENVIRONMENT}")

print()
print("Persistent S3 paths")
print(f"Project root          : {PROJECT_ROOT}")
print(f"Landing               : {LANDING_RAW_ROOT}")
print(f"Dataset registry      : {DATASET_REGISTRY_PATH}")
print(f"Manifests             : {MANIFEST_ROOT}")
print(f"Acquisition metadata  : {ACQUISITION_METADATA_PATH}")

print()
print("Driver-local workspace")
print(f"Downloads             : {DOWNLOAD_PATH}")
print(f"Local manifests       : {MANIFEST_LOCAL_PATH}")

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

# ======================================================
# Read and Validate the Persistent Dataset Registry
# ======================================================

if not STORAGE_CONNECTION_OK:
    raise RuntimeError(
        "Project storage validation did not succeed."
    )

try:
    registry_df = spark.read.parquet(
        DATASET_REGISTRY_PATH
    )
except Exception as exc:
    raise RuntimeError(
        "Dataset registry is unavailable. "
        "Run 03_dataset_registry first."
    ) from exc


required_registry_columns = {
    "dataset_id",
    "dataset_name",
    "dataset_key",
    "dataset_version",
    "dataset_owner",
    "source_type",
    "source_location",
    "source_reference",
    "source_format",
    "landing_folder",
    "enabled",
    "status",
}

missing_columns = required_registry_columns.difference(
    registry_df.columns
)

if missing_columns:
    raise ValueError(
        "Dataset registry is missing required columns: "
        f"{sorted(missing_columns)}"
    )


enabled_registry_df = registry_df.filter(
    F.col("enabled") == F.lit(True)
)

if enabled_registry_df.limit(1).count() == 0:
    raise ValueError(
        "The dataset registry contains no enabled datasets."
    )

display(
    enabled_registry_df.orderBy("dataset_id")
)

# COMMAND ----------

# ======================================================
# Validate Acquisition Readiness
# ======================================================

READY_STATUS = "READY_FOR_DOWNLOAD"

ready_registry_df = enabled_registry_df.filter(
    (F.col("status") == READY_STATUS)
    & F.col("source_location").isNotNull()
    & (F.trim(F.col("source_location")) != "")
    & F.col("source_reference").isNotNull()
    & (F.trim(F.col("source_reference")) != "")
)

not_ready_registry_df = enabled_registry_df.filter(
    (F.col("status") != READY_STATUS)
    | F.col("source_location").isNull()
    | (F.trim(F.col("source_location")) == "")
    | F.col("source_reference").isNull()
    | (F.trim(F.col("source_reference")) == "")
)

not_ready_count = not_ready_registry_df.count()
ready_count = ready_registry_df.count()

if not_ready_count > 0:
    print(
        f"{not_ready_count} enabled dataset(s) are not ready "
        "for acquisition."
    )
    display(
        not_ready_registry_df.orderBy("dataset_id")
    )
else:
    print(
        "All enabled datasets are ready for acquisition."
    )

if ready_count == 0:
    raise ValueError(
        "No enabled datasets are ready for acquisition."
    )

print(
    f"{ready_count} dataset(s) are ready for download."
)

display(
    ready_registry_df.orderBy("dataset_id")
)

# COMMAND ----------

# ======================================================
# Build Persistent Locations from Registry Metadata
# ======================================================

landing_locations_df = ready_registry_df.select(
    "dataset_id",
    "dataset_name",
    "dataset_key",
    "source_type",
    "source_reference",
    "source_format",
    "landing_folder",
    F.concat(
        F.lit(f"{LANDING_RAW_ROOT}/"),
        F.col("landing_folder"),
    ).alias("raw_path"),
    F.concat(
        F.lit(f"{ACQUISITION_METADATA_PATH}/"),
        F.col("landing_folder"),
    ).alias("metadata_path"),
    F.concat(
        F.lit(f"{ACQUISITION_METADATA_PATH}/"),
        F.col("landing_folder"),
        F.lit("/validation"),
    ).alias("validation_path"),
)

display(
    landing_locations_df.orderBy("dataset_id")
)

# COMMAND ----------

# ======================================================
# Validate Persistent Path Configuration
# ======================================================

expected_prefixes = {
    "raw_path": f"{LANDING_RAW_ROOT}/",
    "metadata_path": f"{ACQUISITION_METADATA_PATH}/",
    "validation_path": f"{ACQUISITION_METADATA_PATH}/",
}

for row in landing_locations_df.collect():
    dataset_key = row["dataset_key"]

    for path_name, expected_prefix in expected_prefixes.items():
        path = row[path_name]

        if not path.startswith(expected_prefix):
            raise RuntimeError(
                f"Invalid {path_name} for dataset "
                f"'{dataset_key}': {path}"
            )

        if ".." in path:
            raise RuntimeError(
                f"Unsafe relative path segment detected for "
                f"dataset '{dataset_key}': {path}"
            )

print(
    "Registry validation and persistent-path validation "
    "completed successfully."
)

# COMMAND ----------

# MAGIC %pip install --upgrade kagglehub

# COMMAND ----------

# MAGIC %md
# MAGIC ## Current checkpoint
# MAGIC
# MAGIC The DataCo SMART Supply Chain dataset should appear in `ready_registry_df` with:
# MAGIC
# MAGIC - `source_type = Kaggle`
# MAGIC - `status = READY_FOR_DOWNLOAD`
# MAGIC - a valid Kaggle webpage in `source_location`
# MAGIC - a valid Kaggle identifier in `source_reference`
# MAGIC - a registry-controlled `landing_folder`
# MAGIC
# MAGIC The following cells download the public Kaggle artifacts into temporary driver storage. After download validation, Section 2 persists those files unchanged into the S3 `Landing/raw` zone.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Kaggle Dataset Acquisition
# MAGIC
# MAGIC Download acquisition-ready public Kaggle datasets into temporary
# MAGIC Databricks storage.
# MAGIC
# MAGIC The files will be inspected before they are copied unchanged into the
# MAGIC S3 Landing/raw location.

# COMMAND ----------

from pathlib import Path
import shutil

import kagglehub

# COMMAND ----------

def download_kaggle_dataset(
    dataset_key: str,
    source_reference: str,
) -> Path:
    """
    Download one public Kaggle dataset into temporary driver storage.

    Parameters
    ----------
    dataset_key:
        Internal project identifier for the dataset.

    source_reference:
        Kaggle dataset handle in owner/dataset-slug format.

    Returns
    -------
    Path
        Local directory containing the downloaded dataset files.
    """

    download_root = DOWNLOAD_PATH / dataset_key

    # Remove a previous temporary download so execution is reproducible.
    if download_root.exists():
        shutil.rmtree(download_root)

    download_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    downloaded_path = kagglehub.dataset_download(
        handle=source_reference,
        output_dir=str(download_root),
        force_download=True,
    )

    resolved_path = Path(downloaded_path)

    if not resolved_path.exists():
        raise RuntimeError(
            f"Kaggle download path does not exist: {resolved_path}"
        )

    return resolved_path

# COMMAND ----------

ready_datasets = ready_registry_df.collect()

if len(ready_datasets) != 1:
    raise ValueError(
        "This prototype currently expects exactly one "
        "acquisition-ready dataset."
    )

dataset_config = ready_datasets[0]

dataset_key = dataset_config["dataset_key"]
landing_folder = dataset_config["landing_folder"]
source_type = dataset_config["source_type"]
source_reference = dataset_config["source_reference"]

if source_type.strip().lower() != "kaggle":
    raise ValueError(
        f"Unsupported source type for this prototype: {source_type}"
    )

local_download_path = download_kaggle_dataset(
    dataset_key=dataset_key,
    source_reference=source_reference,
)

print(f"Dataset downloaded to: {local_download_path}")

# COMMAND ----------

downloaded_files = sorted(
    path
    for path in local_download_path.rglob("*")
    if path.is_file()
)

if not downloaded_files:
    raise RuntimeError(
        f"No files were downloaded to {local_download_path}"
    )

print(f"Downloaded files: {len(downloaded_files)}")

for file_path in downloaded_files:
    size_mb = file_path.stat().st_size / (1024 * 1024)

    print(
        f"{file_path.name:60} "
        f"{size_mb:10.2f} MB"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC # Implementation 04 — Section 2: Enterprise Landing Manager
# MAGIC
# MAGIC ## Business objective
# MAGIC
# MAGIC Persist validated source artifacts from temporary driver storage into the project’s durable S3 `Landing/raw` zone.
# MAGIC
# MAGIC The section is provider-independent. It receives local files and a registry-controlled Landing folder; it does not contain Kaggle-specific logic.
# MAGIC
# MAGIC ### Flow
# MAGIC
# MAGIC `Validated download → Storage services → Landing manager → Persistent-file validation`

# COMMAND ----------

# ============================================================
# Section 2.1 — Enterprise Storage Services
# ============================================================

from pathlib import Path
from typing import Any


def create_directory(path: str) -> None:
    """
    Ensure that a persistent storage directory is accessible.
    """

    created = dbutils.fs.mkdirs(path)

    if created is False:
        raise RuntimeError(
            f"Unable to create persistent directory: {path}"
        )

    logger.info(
        "Persistent directory ready | path=%s",
        path,
    )


def copy_file(
    source: Path,
    destination: str,
) -> None:
    """
    Copy one Workspace-staged file into persistent storage.

    Workspace files use file:/Workspace/... and are accessible
    to dbutils.fs on supported Databricks Serverless environments.
    """

    if not source.exists():
        raise FileNotFoundError(
            f"Workspace source file does not exist: {source}"
        )

    if not source.is_file():
        raise ValueError(
            f"Workspace source path is not a file: {source}"
        )

    # Remove the previous object so repeated execution is idempotent.
    try:
        dbutils.fs.rm(
            destination,
            recurse=False,
        )
    except Exception:
        pass

    source_uri = f"file:{source}"

    copied = dbutils.fs.cp(
        source_uri,
        destination,
    )

    if copied is False:
        raise RuntimeError(
            f"Unable to copy {source_uri} to {destination}"
        )

    logger.info(
        "File copied | "
        "source=%s | destination=%s | size_bytes=%s",
        source_uri,
        destination,
        source.stat().st_size,
    )


def list_files(path: str) -> list[Any]:
    """
    List files from a persistent storage directory.
    """

    return list(
        dbutils.fs.ls(path)
    )

# COMMAND ----------

# ============================================================
# Section 2.2 — Landing Path Builder
# ============================================================


def build_landing_path(
    landing_folder: str,
) -> str:
    """Build a safe registry-controlled Landing/raw path."""

    normalized_folder = landing_folder.strip().strip("/")

    if not normalized_folder:
        raise ValueError(
            "landing_folder must not be empty."
        )

    if ".." in normalized_folder:
        raise ValueError(
            f"Unsafe landing_folder: {landing_folder}"
        )

    return f"{LANDING_RAW_ROOT}/{normalized_folder}"

# COMMAND ----------

# ============================================================
# Section 2.3 — Landing File Copier
# ============================================================


def copy_file_to_landing(
    local_file: Path,
    landing_path: str,
) -> str:
    """Copy one source artifact into its Landing directory."""

    destination = f"{landing_path}/{local_file.name}"

    copy_file(
        source=local_file,
        destination=destination,
    )

    return destination

# COMMAND ----------

# ============================================================
# Section 2.4 — Landing Validation
# ============================================================


def validate_landing_files(
    landing_path: str,
    expected_files: list[Path],
) -> list[Any]:
    """Validate Landing filenames and byte sizes against local files."""

    landing_entries = [
        entry
        for entry in list_files(landing_path)
        if not entry.isDir()
    ]

    actual_by_name = {
        entry.name.rstrip("/"): entry
        for entry in landing_entries
    }

    expected_by_name = {
        path.name: path
        for path in expected_files
    }

    missing_names = sorted(
        set(expected_by_name) - set(actual_by_name)
    )
    unexpected_names = sorted(
        set(actual_by_name) - set(expected_by_name)
    )

    if missing_names or unexpected_names:
        raise RuntimeError(
            "Landing filename validation failed | "
            f"missing={missing_names} | "
            f"unexpected={unexpected_names}"
        )

    size_mismatches = []

    for name, local_path in expected_by_name.items():
        local_size = local_path.stat().st_size
        landing_size = actual_by_name[name].size

        if local_size != landing_size:
            size_mismatches.append(
                {
                    "file": name,
                    "local_size": local_size,
                    "landing_size": landing_size,
                }
            )

    if size_mismatches:
        raise RuntimeError(
            "Landing file-size validation failed: "
            f"{size_mismatches}"
        )

    logger.info(
        "Landing validation successful | path=%s | files=%s",
        landing_path,
        len(landing_entries),
    )

    return landing_entries

# COMMAND ----------

# ============================================================
# Section 2.5 — Enterprise Landing Manager
# ============================================================


def copy_dataset_to_landing(
    dataset_key: str,
    landing_folder: str,
    downloaded_files: list[Path],
) -> str:
    """Persist one acquired dataset into S3 Landing/raw."""

    if not downloaded_files:
        raise ValueError(
            f"No downloaded files supplied for dataset: {dataset_key}"
        )

    landing_path = build_landing_path(
        landing_folder=landing_folder,
    )

    create_directory(landing_path)

    for local_file in downloaded_files:
        copy_file_to_landing(
            local_file=local_file,
            landing_path=landing_path,
        )

    validate_landing_files(
        landing_path=landing_path,
        expected_files=downloaded_files,
    )

    logger.info(
        "Dataset persisted to Landing | dataset_key=%s | path=%s",
        dataset_key,
        landing_path,
    )

    return landing_path

# COMMAND ----------

# ============================================================
# Section 2.6 — Execute and Validate Landing Persistence
# ============================================================

landing_path = copy_dataset_to_landing(
    dataset_key=dataset_key,
    landing_folder=landing_folder,
    downloaded_files=downloaded_files,
)

landing_files = validate_landing_files(
    landing_path=landing_path,
    expected_files=downloaded_files,
)

print()
print("=" * 60)
print("Enterprise Landing Completed")
print("=" * 60)
print(f"Dataset key : {dataset_key}")
print(f"Landing path: {landing_path}")
print(f"Files       : {len(landing_files)}")
print()

for entry in sorted(landing_files, key=lambda item: item.name):
    size_mb = entry.size / (1024 * 1024)
    print(f"{entry.name:60} {size_mb:10.2f} MB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Implementation 04 checkpoint
# MAGIC
# MAGIC The acquisition workflow now completes the following path:
# MAGIC
# MAGIC `Dataset Registry → Kaggle download → Local validation → S3 Landing/raw → Persistent validation`
# MAGIC
# MAGIC The next section will generate an acquisition manifest containing dataset identity, source metadata, file names, byte sizes, checksums, acquisition timestamps, and the final Landing location.

# COMMAND ----------

# ============================================================
# Section 3.1 — Enterprise Manifest Models
# ============================================================

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ManifestFile:
    """
    Metadata describing one acquired file.
    """

    name: str

    extension: str

    mime_type: str

    size_bytes: int

    sha256: str

    landing_path: str


@dataclass(frozen=True)
class AcquisitionManifest:
    """
    Enterprise acquisition manifest.
    """

    manifest: dict[str, Any]

    pipeline: dict[str, Any]

    acquisition: dict[str, Any]

    dataset: dict[str, Any]

    provider: dict[str, Any]

    landing: dict[str, Any]

    files: list[ManifestFile]

    statistics: dict[str, Any]


print("Enterprise Manifest models initialized.")

# COMMAND ----------

# ============================================================
# Section 3.2 — Enterprise Checksum Service
# ============================================================

from pathlib import Path


CHECKSUM_ALGORITHM = "sha256"
CHECKSUM_BUFFER_SIZE = 1024 * 1024  # 1 MB


def compute_sha256(
    file_path: Path,
) -> str:
    """
    Compute the SHA-256 checksum of a file.

    Parameters
    ----------
    file_path
        Local file path.

    Returns
    -------
    str
        SHA-256 hexadecimal digest.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    digest = hashlib.sha256()

    with file_path.open("rb") as stream:

        while True:

            chunk = stream.read(
                CHECKSUM_BUFFER_SIZE
            )

            if not chunk:
                break

            digest.update(chunk)

    checksum = digest.hexdigest()

    logger.info(
        "Checksum computed | file=%s | algorithm=%s",
        file_path.name,
        CHECKSUM_ALGORITHM,
    )

    return checksum


print(
    "Enterprise Checksum Service initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.3 — Enterprise File Metadata Builder
# ============================================================

import mimetypes
from pathlib import Path


def build_manifest_file(
    file_path: Path,
    landing_path: str,
) -> ManifestFile:
    """
    Build enterprise metadata for one acquired file.

    Parameters
    ----------
    file_path
        Local workspace file.

    landing_path
        Persistent Landing location in S3.

    Returns
    -------
    ManifestFile
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    mime_type, _ = mimetypes.guess_type(
        file_path.name
    )

    if mime_type is None:
        mime_type = "application/octet-stream"

    manifest_file = ManifestFile(
        name=file_path.name,
        extension=file_path.suffix.lower(),
        mime_type=mime_type,
        size_bytes=file_path.stat().st_size,
        sha256=compute_sha256(file_path),
        landing_path=landing_path,
    )

    logger.info(
        "Manifest metadata built | file=%s",
        file_path.name,
    )

    return manifest_file


print(
    "Enterprise File Metadata Builder initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.4 — Enterprise Manifest Builder
# ============================================================

from dataclasses import asdict
from datetime import datetime, timezone
import uuid


def build_acquisition_manifest(
    *,
    dataset_name: str,
    dataset_key: str,
    dataset_version: str,
    provider: str,
    source_reference: str,
    landing_path: str,
    downloaded_files: list[Path],
) -> AcquisitionManifest:
    """
    Build the enterprise acquisition manifest.
    """

    manifest_files: list[ManifestFile] = []

    total_bytes = 0

    for file_path in downloaded_files:

        file_landing_path = (
            f"{landing_path}/{file_path.name}"
        )

        metadata = build_manifest_file(
            file_path=file_path,
            landing_path=file_landing_path,
        )

        manifest_files.append(metadata)

        total_bytes += metadata.size_bytes

    manifest = AcquisitionManifest(

        manifest={

            "manifest_id": str(uuid.uuid4()),

            "manifest_version": "1.0",

            "created_utc": datetime.now(
                timezone.utc
            ).isoformat(),

        },

        pipeline={

            "name": PIPELINE_NAME,

            "version": PIPELINE_VERSION,

        },

        acquisition={

            "status": "SUCCESS",

            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),

        },

        dataset={

            "name": dataset_name,

            "key": dataset_key,

            "version": dataset_version,

        },

        provider={

            "name": provider,

            "source_reference": source_reference,

        },

        landing={

            "path": landing_path,

        },

        files=manifest_files,

        statistics={

            "file_count": len(manifest_files),

            "total_size_bytes": total_bytes,

        },

    )

    logger.info(

        "Enterprise manifest built | dataset=%s | files=%s",

        dataset_key,

        len(manifest_files),

    )

    return manifest


print(
    "Enterprise Manifest Builder initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.5.1 — Enterprise Manifest Path Service
# ============================================================

from datetime import datetime, timezone


MANIFEST_EXTENSION = ".json"


def get_manifest_directory(
    dataset_key: str,
) -> str:
    """
    Return the persistent S3 directory for a dataset's manifests.
    """

    return (
        f"{MANIFEST_ROOT}/"
        f"{dataset_key}"
    )


def generate_manifest_filename() -> str:
    """
    Generate a timestamped manifest filename.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    return (
        f"{timestamp}_manifest"
        f"{MANIFEST_EXTENSION}"
    )


def get_manifest_path(
    dataset_key: str,
) -> str:
    """
    Return the full S3 manifest path.
    """

    directory = get_manifest_directory(
        dataset_key
    )

    filename = generate_manifest_filename()

    return f"{directory}/{filename}"


print(
    "Enterprise Manifest Path Service initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.5.2 — Enterprise Manifest Serialization Service
# ============================================================

from dataclasses import asdict
import json


def serialize_manifest(
    manifest: AcquisitionManifest,
) -> str:
    """
    Serialize an AcquisitionManifest to formatted JSON.
    """

    manifest_dict = asdict(manifest)

    manifest_json = json.dumps(
        manifest_dict,
        indent=4,
        sort_keys=False,
    )

    logger.info(
        "Manifest serialized | bytes=%s",
        len(manifest_json.encode("utf-8")),
    )

    return manifest_json


print(
    "Enterprise Manifest Serialization Service initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.5.3 — Enterprise Manifest Persistence Service
# ============================================================


def persist_manifest(
    *,
    manifest: AcquisitionManifest,
    dataset_key: str,
) -> str:
    """
    Serialize and persist an acquisition manifest directly to S3.

    Returns
    -------
    str
        Full S3 path of the persisted manifest.
    """

    # --------------------------------------------------------
    # Build persistent destination
    # --------------------------------------------------------

    manifest_directory = get_manifest_directory(
        dataset_key
    )

    manifest_path = get_manifest_path(
        dataset_key
    )

    create_directory(
        manifest_directory
    )

    # --------------------------------------------------------
    # Serialize manifest
    # --------------------------------------------------------

    manifest_json = serialize_manifest(
        manifest
    )

    # --------------------------------------------------------
    # Write directly to S3
    # --------------------------------------------------------

    written = dbutils.fs.put(
        manifest_path,
        manifest_json,
        overwrite=False,
    )

    if written is False:
        raise RuntimeError(
            f"Unable to persist manifest: {manifest_path}"
        )

    logger.info(
        "Manifest persisted | "
        "dataset=%s | path=%s | size_bytes=%s",
        dataset_key,
        manifest_path,
        len(manifest_json.encode("utf-8")),
    )

    return manifest_path


print(
    "Enterprise Manifest Persistence Service initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.6 — Enterprise Manifest Validation
# ============================================================

import json


def validate_manifest(
    *,
    manifest_path: str,
    manifest: AcquisitionManifest,
) -> None:
    """
    Validate the actual persisted acquisition manifest in S3.
    """

    # --------------------------------------------------------
    # 1. Read persisted manifest
    # --------------------------------------------------------

    try:
        persisted_json = dbutils.fs.head(
            manifest_path,
            1024 * 1024,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Manifest does not exist or is unreadable: "
            f"{manifest_path}"
        ) from exc

    if not persisted_json.strip():
        raise RuntimeError(
            "Persisted manifest is empty."
        )

    # --------------------------------------------------------
    # 2. Parse persisted JSON
    # --------------------------------------------------------

    try:
        parsed_manifest = json.loads(
            persisted_json
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Persisted manifest contains invalid JSON."
        ) from exc

    # --------------------------------------------------------
    # 3. Validate required sections
    # --------------------------------------------------------

    required_sections = {
        "manifest",
        "pipeline",
        "acquisition",
        "dataset",
        "provider",
        "landing",
        "files",
        "statistics",
    }

    missing_sections = sorted(
        required_sections
        - parsed_manifest.keys()
    )

    if missing_sections:
        raise RuntimeError(
            "Missing manifest sections: "
            + ", ".join(missing_sections)
        )

    # --------------------------------------------------------
    # 4. Validate dataset identity
    # --------------------------------------------------------

    persisted_dataset_key = (
        parsed_manifest["dataset"].get("key")
    )

    expected_dataset_key = (
        manifest.dataset.get("key")
    )

    if persisted_dataset_key != expected_dataset_key:
        raise RuntimeError(
            "Persisted manifest dataset key mismatch."
        )

    # --------------------------------------------------------
    # 5. Validate files and statistics
    # --------------------------------------------------------

    persisted_files = parsed_manifest["files"]

    if not persisted_files:
        raise RuntimeError(
            "Persisted manifest contains no files."
        )

    file_count = parsed_manifest[
        "statistics"
    ].get("file_count")

    if file_count != len(persisted_files):
        raise RuntimeError(
            "Manifest file count does not match "
            "the files collection."
        )

    total_size = parsed_manifest[
        "statistics"
    ].get("total_size_bytes")

    calculated_total_size = sum(
        file_metadata.get("size_bytes", 0)
        for file_metadata in persisted_files
    )

    if total_size != calculated_total_size:
        raise RuntimeError(
            "Manifest total size does not match "
            "the sum of file sizes."
        )

    if total_size <= 0:
        raise RuntimeError(
            "Manifest total size must be positive."
        )

    logger.info(
        "Persisted manifest validation successful | "
        "path=%s | files=%s | total_size_bytes=%s",
        manifest_path,
        file_count,
        total_size,
    )


print(
    "Enterprise Manifest Validation initialized."
)

# COMMAND ----------

# ============================================================
# Section 3.7 — Enterprise Manifest Execution
# ============================================================

dataset_name = dataset_config["dataset_name"]
dataset_key = dataset_config["dataset_key"]
dataset_version = dataset_config["dataset_version"]
source_type = dataset_config["source_type"]
source_reference = dataset_config["source_reference"]

manifest = build_acquisition_manifest(
    dataset_name=dataset_name,
    dataset_key=dataset_key,
    dataset_version=dataset_version,
    provider=source_type,
    source_reference=source_reference,
    landing_path=landing_path,
    downloaded_files=downloaded_files,
)

manifest_path = persist_manifest(
    manifest=manifest,
    dataset_key=dataset_key,
)

validate_manifest(
    manifest_path=manifest_path,
    manifest=manifest,
)

print()
print("=" * 70)
print("Enterprise Manifest Completed")
print("=" * 70)

print(f"Dataset       : {dataset_key}")
print(f"Manifest Path : {manifest_path}")
print(f"Files         : {manifest.statistics['file_count']}")
print(
    f"Total Size    : "
    f"{manifest.statistics['total_size_bytes']:,} bytes"
)

print("=" * 70)

# COMMAND ----------

# MAGIC %md
# MAGIC # Section 04 — Bronze Layer
# MAGIC
# MAGIC Convert validated Landing files into standardized Parquet datasets.
# MAGIC
# MAGIC Bronze responsibilities:
# MAGIC
# MAGIC - Preserve all source records
# MAGIC - Standardize column names
# MAGIC - Add technical lineage metadata
# MAGIC - Write idempotent Parquet outputs to S3
# MAGIC - Validate persisted Bronze datasets

# COMMAND ----------

# ============================================================
# Section 04.1 — Bronze Layer Utilities
# ============================================================

import re
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


SUPPORTED_BRONZE_FORMATS = {
    "csv",
    "json",
    "parquet",
}

PRIMARY_SOURCE_FILES = {
    "dataco_supply_chain": "DataCoSupplyChainDataset.csv",
}

def normalize_column_name(column_name: str) -> str:
    """
    Convert a source column name into a stable Spark-compatible name.
    """

    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    normalized = normalized.strip("_")

    if not normalized:
        raise ValueError(
            f"Column name cannot be normalized: {column_name!r}"
        )

    return normalized


def standardize_column_names(df: DataFrame) -> DataFrame:
    """
    Normalize all source column names and prevent duplicate names.
    """

    normalized_columns = [
        normalize_column_name(column_name)
        for column_name in df.columns
    ]

    duplicates = sorted(
        {
            column_name
            for column_name in normalized_columns
            if normalized_columns.count(column_name) > 1
        }
    )

    if duplicates:
        raise ValueError(
            "Column normalization produced duplicate columns: "
            f"{duplicates}"
        )

    return df.toDF(*normalized_columns)


def read_landing_dataset(
    *,
    landing_path: str,
    source_format: str,
    dataset_key: str,
) -> DataFrame:
    """
    Read the primary business file for one validated Landing dataset.
    """

    normalized_format = source_format.strip().lower()

    if normalized_format not in SUPPORTED_BRONZE_FORMATS:
        raise ValueError(
            f"Unsupported Bronze source format: {source_format!r}. "
            f"Supported formats: {sorted(SUPPORTED_BRONZE_FORMATS)}"
        )

    primary_file_name = PRIMARY_SOURCE_FILES.get(dataset_key)

    if not primary_file_name:
        raise ValueError(
            "No primary source file is configured for dataset: "
            f"{dataset_key}"
        )

    source_path = f"{landing_path.rstrip('/')}/{primary_file_name}"

    print(f"Primary source file: {source_path}")

    if normalized_format == "csv":
        return (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .option("multiLine", True)
            .option("escape", '"')
            .option("quote", '"')
            .option("mode", "FAILFAST")
            .csv(source_path)
        )

    if normalized_format == "json":
        return (
            spark.read
            .option("multiLine", True)
            .option("mode", "FAILFAST")
            .json(source_path)
        )

    return spark.read.parquet(source_path)


def add_bronze_metadata(
    df: DataFrame,
    *,
    dataset_key: str,
    dataset_name: str,
    dataset_version: str,
) -> DataFrame:
    """
    Add technical lineage columns without changing source records.
    """

    return (
        df
        .withColumn(
            "_source_file",
            F.col("_metadata.file_path"),
        )
        .withColumn(
            "_dataset_key",
            F.lit(dataset_key),
        )
        .withColumn(
            "_dataset_name",
            F.lit(dataset_name),
        )
        .withColumn(
            "_dataset_version",
            F.lit(dataset_version),
        )
        .withColumn(
            "_bronze_ingested_at_utc",
            F.current_timestamp(),
        )
        .withColumn(
            "_bronze_load_date",
            F.current_date(),
        )
    )


def build_bronze_path(dataset_key: str) -> str:
    """
    Return the persistent Bronze S3 path for one dataset.
    """

    normalized_key = normalize_column_name(dataset_key)

    return f"{BRONZE_ROOT}/{normalized_key}"


def write_bronze_dataset(
    df: DataFrame,
    bronze_path: str,
) -> None:
    """
    Persist a complete Bronze snapshot as Parquet.

    Overwrite is intentional because the current public source dataset
    is registry-versioned and processed as a reproducible snapshot.
    """

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(bronze_path)
    )


def validate_bronze_dataset(
    *,
    bronze_path: str,
    expected_row_count: int,
    expected_columns: list[str],
) -> dict[str, Any]:
    """
    Read the persisted Bronze dataset and validate its integrity.
    """

    persisted_df = spark.read.parquet(bronze_path)

    actual_row_count = persisted_df.count()
    actual_columns = persisted_df.columns

    missing_columns = sorted(
        set(expected_columns) - set(actual_columns)
    )

    if actual_row_count != expected_row_count:
        raise RuntimeError(
            "Bronze row-count validation failed. "
            f"Expected {expected_row_count:,}; "
            f"found {actual_row_count:,}."
        )

    if missing_columns:
        raise RuntimeError(
            "Bronze schema validation failed. "
            f"Missing columns: {missing_columns}"
        )

    return {
        "bronze_path": bronze_path,
        "row_count": actual_row_count,
        "column_count": len(actual_columns),
        "status": "PASSED",
    }


def create_bronze_dataset(
    dataset: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute the complete Landing-to-Bronze process for one dataset.
    """

    dataset_key = dataset["dataset_key"]
    dataset_name = dataset["dataset_name"]
    dataset_version = dataset["dataset_version"]
    source_format = dataset["source_format"]
    landing_folder = dataset["landing_folder"]

    landing_path = build_landing_path(landing_folder)
    bronze_path = build_bronze_path(dataset_key)

    landing_df = read_landing_dataset(
        landing_path=landing_path,
        source_format=source_format,
        dataset_key=dataset_key,
    )

    bronze_df = standardize_column_names(landing_df)

    bronze_df = add_bronze_metadata(
        bronze_df,
        dataset_key=dataset_key,
        dataset_name=dataset_name,
        dataset_version=dataset_version,
    )

    expected_row_count = bronze_df.count()
    expected_columns = bronze_df.columns

    if expected_row_count == 0:
        raise RuntimeError(
            f"Bronze creation rejected empty dataset: {dataset_key}"
        )

    write_bronze_dataset(
        df=bronze_df,
        bronze_path=bronze_path,
    )

    validation = validate_bronze_dataset(
        bronze_path=bronze_path,
        expected_row_count=expected_row_count,
        expected_columns=expected_columns,
    )

    return {
        "dataset_key": dataset_key,
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        **validation,
    }

# COMMAND ----------

# ============================================================
# Section 04.2 — Execute Bronze Processing
# ============================================================

bronze_results: list[dict[str, Any]] = []

registry_records = [
    row.asDict(recursive=True)
    for row in ready_registry_df.collect()
]

if not registry_records:
    raise RuntimeError(
        "No acquisition-ready datasets are available for Bronze processing."
    )

for dataset in registry_records:
    dataset_key = dataset["dataset_key"]

    print()
    print("=" * 70)
    print(f"Creating Bronze dataset: {dataset_key}")
    print("=" * 70)

    result = create_bronze_dataset(dataset)
    bronze_results.append(result)

    print(f"Status:       {result['status']}")
    print(f"Rows:         {result['row_count']:,}")
    print(f"Columns:      {result['column_count']}")
    print(f"Bronze path:  {result['bronze_path']}")

# COMMAND ----------

# ============================================================
# Section 04.3 — Bronze Processing Summary
# ============================================================

bronze_summary_df = spark.createDataFrame(bronze_results)

display(
    bronze_summary_df.select(
        "dataset_key",
        "dataset_name",
        "dataset_version",
        "row_count",
        "column_count",
        "status",
        "bronze_path",
    )
)

failed_bronze_datasets = [
    result
    for result in bronze_results
    if result["status"] != "PASSED"
]

if failed_bronze_datasets:
    raise RuntimeError(
        "One or more Bronze datasets failed validation: "
        f"{failed_bronze_datasets}"
    )

print()
print("=" * 70)
print("BRONZE LAYER COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"Datasets processed: {len(bronze_results)}")
print(
    "Total rows written: "
    f"{sum(result['row_count'] for result in bronze_results):,}"
)

# COMMAND ----------

