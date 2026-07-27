# Implementation 05 — Enterprise Parameter Framework

**Status:** Ready for validation  
**Version:** 1.0.0  
**Author:** Issouf KABRE  
**Platform:** AI Workforce Capacity Planning Platform

---

## 1. Business Objective

Create one shared and validated parameter framework for the platform.

The framework must allow business and runtime behavior to change without
embedding variable operational values inside pipeline, forecasting,
capacity-planning, or AI logic.

---

## 2. Scope

Implementation 05 centralizes:

- project identity;
- environment;
- S3 storage paths;
- pipeline defaults;
- forecast defaults and runtime boundaries;
- model-selection defaults;
- capacity-planning defaults;
- AI-assistant defaults;
- shared validation utilities.

---

## 3. Architecture Decision

Notebook `00_project_setup` remains the platform bootstrap and configuration
center.

Downstream notebooks continue to load it through `%run`.

Existing global constants remain available to preserve compatibility with the
validated `02_data_pipeline`.

The active forecast horizon is resolved at runtime. Notebook 00 provides only
its default and validation limits.

---

## 4. Runtime Contract

The default forecast horizon is 14 days.

The accepted runtime range is 1 through 90 days.

A future forecasting notebook may supply any valid horizon in that range
without modifying model implementation code.

---

## 5. Compatibility Contract

The following existing constants remain available:

- `PROJECT_NAME`
- `PROJECT_KEY`
- `PROJECT_VERSION`
- `ENVIRONMENT`
- `S3_BUCKET`
- `PROJECT_ROOT`
- `BRONZE_ROOT`
- `SILVER_ROOT`
- `GOLD_ROOT`
- `METADATA_ROOT`
- `REGISTRY_ROOT`
- `MANIFEST_ROOT`
- `VALIDATION_ROOT`
- `PIPELINE_LOG_ROOT`
- `MODEL_ROOT`
- `DATASET_REGISTRY_PATH`
- `PROJECT_PATHS`

---

## 6. Validation

Validation succeeds when:

1. all configuration mappings contain required keys;
2. forecast boundaries satisfy minimum <= default <= maximum;
3. numeric parameters fall inside accepted ranges;
4. the project S3 root is accessible;
5. the execution summary reports:
   - Configuration status: PASSED
   - Storage status: PASSED
   - Runtime status: READY
6. `02_data_pipeline` still completes successfully after importing the updated
   setup notebook.

---

## 7. Rollback

The previous validated `00_project_setup` remains recoverable through Git
history.

Do not commit the replacement until both Notebook 00 and Notebook 02 pass.
