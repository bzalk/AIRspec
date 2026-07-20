# AIRspec Changelog

## 1.1.0-draft

AIRspec 1.1 adds a general reactive interaction model while preserving the 1.0 security boundary and stable 1.0 schema URL.

### Added

* **1.1 amendment:** structured row-level `derived` fields and post-aggregation calc-form metrics. Arithmetic is a closed JSON tree (`add`, `subtract`, `multiply`, `divide`), never a parsed string or identifier-encoded formula; metric aliases are now required and output names are deterministic.
* **1.1 amendment:** `scale.reverse` for mirrored quantitative, logarithmic, band, and ordinal axes. This is backward compatible; documents that omit it are unchanged, while documents using it require the amended 1.1 schema.
* **1.1 amendment:** defined positional `axis.orient` semantics, including right-edge nominal labels for the center spine of mirrored chart pairs.
* **1.1 amendment:** required mirrored chart halves to declare the same explicit quantitative domain and documented both outer-label and center-spine variants.
* Typed Dataset parameter bindings for `fields`, `field`, `dimensions`, `metrics`, `filters`, `sort`, and `limit`.
* Stable output contracts across Dataset alternatives.
* Whole-graphic parameter bindings for safe presentation switching.
* Selection-qualified interaction events and `selectionClear`.
* `scalar`, `values`, and `range` selection transfer modes.
* Atomic multi-action interactions.
* Dependency, coalescing, cache-key, state-revision, and stale-response requirements.
* AIRspec 1.1 schema, reactive reference sample, design matrix, and conformance fixtures.

### Security

Bindings select only among complete, predeclared, independently valid alternatives. Derived arithmetic is a closed, bounded JSON algebra compiled by the Data Broker from allowlisted operators and catalog-mapped fields. AIRspec 1.1 does not add string expressions, templates, identifier-encoded formulas, arbitrary property paths, JSON Patch, dynamic sources, dynamic operations, client-supplied Dataset definitions, or chart-runtime event handlers.

## 1.0.0-draft

Initial public draft: document structure, parameters, logical datasets, layout and components, AIRMark, formatting, theming, interactions, validation layers, security requirements, and conformance classes.
