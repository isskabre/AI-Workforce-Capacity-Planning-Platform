# ADR-002 — Parameter-Driven Platform Configuration

**Status:** Accepted  
**Date:** 2026-07-27  
**Platform:** AI Workforce Capacity Planning Platform

---

## Context

Forecast horizons, storage locations, model settings, capacity assumptions,
and AI behavior may change across environments or business use cases.

Embedding these values directly inside implementation logic would create
duplication and require code changes for normal operational configuration.

---

## Decision

Use `00_project_setup` as the centralized platform parameter framework.

Separate:

- static platform defaults;
- runtime parameters;
- forecasting logic;
- capacity-planning policy;
- AI explanation behavior.

The active forecast horizon is supplied at runtime and validated against
configured minimum and maximum values.

---

## Consequences

### Positive

- downstream notebooks use consistent parameters;
- the forecast horizon can change without model-code changes;
- configuration validation fails early;
- the current data pipeline remains backward compatible;
- future DEV, TEST, and PROD overrides can be added cleanly.

### Trade-offs

- downstream notebooks depend on the setup notebook contract;
- configuration changes require validation against existing consumers;
- secrets must remain outside this framework.

---

## Rejected Alternative

Hard-code one-day, seven-day, and fourteen-day forecasting paths.

This was rejected because it duplicates logic and restricts future business
planning windows.
