# Implementing AIRspec

**A build guide for engineers and AI coding agents.**

This document turns the specification into a concrete build plan. It is written so you can hand it — together with `AIRspec.md`, `schema/`, `samples/`, and `conformance/` — directly to a coding agent as the primary instruction set for implementing an AIRspec Host inside your application. Fill in the **Project Brief** section first; everything after it is stack-agnostic.

The definition of done is not "it renders the samples." It is: **`conformance/runner.py --cmd <your validator>` passes every case**, and the runtime requirements in Part 4 hold.

---

## Project Brief (fill this in before handing off)

An agent cannot infer these; ambiguity here is the main cause of weak implementations.

```yaml
application:
  frontend: ""        # e.g. React 18 + TypeScript, Vite
  backend: ""         # e.g. Node/Express, .NET 8, Rails — where the Data Broker lives
  chart_runtime: ""   # e.g. Vega-Lite via react-vega, ECharts, bespoke SVG — see Part 5
  auth_model: ""      # how the current viewer + tenant are established server-side

target_conformance_class: "A"   # A first, then AV, then AVI — in that order

data_sources:
  # The real business concepts your reports cover. For each, you will author
  # a Source Catalog entry (schema/1.0/catalog.schema.json) BEFORE any code
  # is written. List them here:
  - ""

routes:
  # Registered route IDs that navigate actions may target (Class AVI):
  - ""

generator:
  provider: ""        # e.g. structured outputs or tool use from your chosen provider
  # The generator receives: the AIRspec JSON Schema, your Source Catalog,
  # your limits, and machine-readable validation errors for self-correction.

limits: {}            # overrides of AIRspec.md §16 defaults, if any
```

---

## Part 1 — Build order

Build in this order; each step is testable before the next begins.

1. **Author the Source Catalog.** Write your catalog conforming to `schema/1.0/catalog.schema.json`. This is a design task, not a coding task: describe logical business concepts, not endpoints (spec §6). Every later step consumes it.
2. **Types.** Generate or hand-write types for the AIRspec document and catalog from the two schemas. One module, no dependencies on the rest of the app.
3. **Validators, layers 1–4** (Part 3). Pure functions: `(document, catalog, policy) → { valid, errors[] }`. No I/O. Wire `conformance/runner.py --cmd` into your test suite now — you will implement against failing conformance cases the way you'd implement against failing unit tests.
4. **Data Broker** (Part 4). The single trusted server endpoint that executes stored datasets.
5. **Renderer** (Part 5). Component registry + layout tree walker + per-component error boundaries.
6. **Persistence.** Reports and immutable report versions (spec §23 is a ready storage model).
7. **Generator loop** (Part 6). Last, because it depends on the catalog, schema, and validator errors all existing.

Class A requires steps 1–7 without charts. Class AV adds the AIRMark path in steps 3 and 5. Class AVI adds interactions in step 5.

---

## Part 2 — Contracts you must not reinterpret

These are the load-bearing rules; everything else has implementation freedom.

* **Documents are configuration.** Never `eval`, template-interpolate, or otherwise execute any string from a document. (Spec §2, §15.)
* **Deny by default.** Unknown non-`x-` properties are rejected, not ignored. (§3.1)
* **Execution references stored versions.** The client sends only `{versionId, datasetId, parameterValues, pagination}` — never a dataset definition. (§7.8, §15.4)
* **Viewer's authorization, server's credentials.** Tenant scoping is applied by the broker independently of document filters; identifiers inside documents are never trusted. (§15.3, §15.5)
* **Graphics never carry data.** The renderer injects rows as the named datasource `airspecData`; resolution order is security overrides → tenant theme → document theme → graphic → renderer defaults. (§10.1)
* **Fail soft per component.** One failing dataset or component must not blank the report. (§2.5, §29)

---

## Part 3 — The validation pipeline

Implement as four ordered, pure stages. Return **machine-readable errors** — the generator's self-correction loop depends on their quality:

```json
{ "layer": 2, "code": "UNKNOWN_DATASET_REF", "path": "/layout/children/1/children/0/datasetId",
  "message": "Component 'revenueMetric' references dataset 'doesNotExist'; defined datasets: totals, orderList." }
```

Include the valid alternatives in messages where cheap (as above) — it measurably improves model self-correction.

**Layer 1 — Schema.** Select the versioned schema matching the document's `airspec` value (`schema/1.0/airspec.schema.json`, `schema/1.1/airspec.schema.json`, and so on) and validate with a draft 2020-12 validator. Do not hand-roll.

**Layer 2 — Semantic.** The checks, exhaustively (each maps to a conformance case):
dataset `source` exists in catalog · every dataset field/dimension/metric field/filter field/sort field exists on its source · aggregations appear in the field's catalog `aggregations` · `timeUnit` only on date/datetime fields with catalog `timeUnits` · filter operators permitted for the field (catalog `operators` or your type defaults) · filter `parameter` refs resolve and are type-compatible · component `datasetId` refs resolve · every component-bound field (metric `valueField`, table columns, encoding `field`s, tooltip fields, interaction `valueFrom`/`recordIdFrom`/params fields) is present in the bound dataset's **output** (list `fields` or aggregate aliases/dimension fields) · component IDs unique; parameter IDs unique; dataset IDs unique · filterBar parameters resolve · interaction `on.component` resolves · navigate `route` is registered in the catalog · selection IDs referenced by `condition` exist in the same graphic.

For AIRspec 1.1, additionally validate every Dataset binding case/default, static-option coverage, unique and type-compatible `equals` values, stable output contracts across alternatives, every graphic-binding alternative, selection-qualified events, transfer-mode compatibility, and atomic action references. Never implement bindings as arbitrary paths or patches.

**Layer 3 — Authorization.** Host-defined. Minimum viable policy (matches `conformance/policy.example.json`): allowed sources per viewer; denied field `classification`s; row/page ceilings. Enforce at validation time AND re-check at every execution — a stored document may outlive a permission grant.

**Layer 4 — AIRMark.** Mostly enforced structurally by the Layer-1 schema (deny by default). Your additional duties: recursively scan every `graphic` for URL-shaped string values and expression-shaped strings regardless of property name; enforce `maxGraphicBytes`, `maxLayerCount`, facet-cell caps; verify layer/facet encodings against the dataset output (a Layer-2-style check that lives here because it's per-graphic).

---

## Part 4 — The Data Broker

One endpoint: `POST /api/reports/{versionId}/datasets/{datasetId}/execute` with `{parameters, page}`.

Execution sequence (spec §18): authenticate → load immutable version → locate dataset → authorize source and fields for **this viewer** → validate parameter values against parameter declarations → translate the logical request via the source's adapter → attach credentials server-side → execute → normalize rows to flat objects keyed by field/alias → strip fields the viewer may not receive → clamp and return `{rows, page, truncated}`.

Write one **adapter interface** (`executeList`, `executeAggregate`, `getDistinctValues`) and one concrete adapter per source. Adapters own the translation from logical requests to your real APIs/queries — renames, pagination stitching, enum mapping. Nothing outside adapters touches real endpoints.

Error responses: structured, user-presentable, and free of internal URLs, stack traces, and credentials (§29). When a limit is exceeded, say which limit and suggest the remedy (narrower range, aggregation).

---

## Part 5 — The Renderer

* A `componentRegistry` mapping each component `type` to a trusted component; unknown types render a placeholder, never crash (§24 has the pattern).
* Recursive layout walker over `layout`; 12-column grid with the responsive span fields; safe defaults for omitted layout values.
* Per-component: loading, empty (`emptyState` pairing), invalid-config, auth-failure, and error states. Component-level error boundaries.
* Dataset loading is keyed by `versionId + datasetId + normalized params + pagination + viewer scope` and deduplicated — two components on one dataset produce one request (§25).
* **Charts (Class AV):** implement AIRMark via an adapter to your chosen chart runtime. The adapter accepts only *validated* graphics, injects broker rows as `airspecData`, applies the §10.1 resolution order, and strips any target-runtime capability the spec prohibits even if the runtime supports it (see `adapters/README.md`). Compiling AIRMark to Vega-Lite is typically ~200–400 lines and the fastest AV path.
  For a portable renderer with no required chart runtime, follow `adapters/framework-agnostic-renderer.md`: keep transforms, scales, axes, geometry, and interaction metadata in a pure layout engine that emits a scene graph, then draw it with a thin platform adapter.
* **Interactions (Class AVI):** a dispatcher from `{component, event, selection?}` to the fixed action vocabulary. Apply AIRspec 1.1 parameter mutations atomically, resolve dependent bindings once, and execute each affected dataset at most once per state revision. `navigate` resolves route IDs through your router registry — never constructs URLs from document content.

---

## Part 6 — The Generator loop

1. Context given to the model: the AIRspec JSON Schema, your Source Catalog, your limits, and (when editing) the current document.
2. Constrained/structured output producing a single JSON document.
3. Run the full validation pipeline. On failure, return the machine-readable errors to the model and retry (cap at ~3 attempts; surface residual errors to the user).
4. On success: store as a new immutable version; render.

For diverging pairs such as population pyramids, tornado charts, and butterfly comparisons, Generators SHOULD build two mirrored charts in adjacent grid cells and set `"scale": {"reverse": true}` on the left chart's quantitative channel. Keep category labels on the outer or shared edge through declarative axis configuration.

Do not give the model credentials, endpoints, URL-fetching tools, or execution tools (§20). Optional but high-value tools to expose instead: `describe_source`, `preview_dataset` (broker-backed, viewer-scoped, row-capped), `validate_document`.

---

## Part 7 — Definition of done

* [ ] `python conformance/runner.py --cmd "<your validator>"` — every manifest case passes
* [ ] The three `samples/` documents render end-to-end against your catalog-equivalent sources (adjust source/field names or add a mapping catalog)
* [ ] Broker rejects a hand-crafted execution request containing an inline dataset definition
* [ ] A document requesting a field the viewer may not see renders everything else and shows a per-component auth error
* [ ] Killing one dataset's backing source degrades only that component
* [ ] Regenerating a report produces a new version; the old version still renders
* [ ] No document string is ever passed to `eval`, `Function`, `innerHTML`, or a template engine with logic
* [ ] Class AV additionally: all `valid/` chart fixtures render; every `invalid/l4-*` fixture is rejected before reaching the chart runtime

---

*Sequence for a first real project: Class A end-to-end with two sources, then AV via a chart-runtime adapter, then AVI. Extract shared libraries only after this survives real use.*
