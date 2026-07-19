# AIRspec Changelog

## 1.1.0-draft

AIRspec 1.1 adds a general reactive interaction model while preserving the 1.0 security boundary and stable 1.0 schema URL.

### Added

* **1.1 amendment:** `scale.reverse` for mirrored quantitative, logarithmic, band, and ordinal axes. This is backward compatible; documents that omit it are unchanged, while documents using it require the amended 1.1 schema.
* Typed Dataset parameter bindings for `fields`, `field`, `dimensions`, `metrics`, `filters`, `sort`, and `limit`.
* Stable output contracts across Dataset alternatives.
* Whole-graphic parameter bindings for safe presentation switching.
* Selection-qualified interaction events and `selectionClear`.
* `scalar`, `values`, and `range` selection transfer modes.
* Atomic multi-action interactions.
* Dependency, coalescing, cache-key, state-revision, and stale-response requirements.
* AIRspec 1.1 schema, reactive reference sample, design matrix, and conformance fixtures.

### Security

Bindings select only among complete, predeclared, independently valid alternatives. AIRspec 1.1 does not add expressions, templates, arbitrary property paths, JSON Patch, dynamic sources, dynamic operations, client-supplied Dataset definitions, or chart-runtime event handlers.

## 1.0.0-draft

Initial public draft: document structure, parameters, logical datasets, layout and components, AIRMark, formatting, theming, interactions, validation layers, security requirements, and conformance classes.
