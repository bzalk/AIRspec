# AI Coding Prompt: Implement AIRspec in Any Framework

Copy everything below the divider into your AI coding tool. Fill in the Project Brief first.

---

You are implementing AIRspec in an existing application. Work directly in the supplied repository and deliver a production-ready vertical slice. Do not merely write an architecture proposal.

## Project Brief

```yaml
project_name: "FILL IN"
language_and_framework: "FILL IN"
package_manager_and_commands: "FILL IN"
client_runtime: "FILL IN"
server_runtime: "FILL IN"
database_or_data_apis: "FILL IN"
authentication_and_authorization: "FILL IN"
existing_routes: "FILL IN"
target_conformance_class: "A, AV, or AVI"
first_source_to_implement: "FILL IN"
first_report_to_render: "FILL IN"
test_typecheck_lint_build_commands: "FILL IN"
```

If a blank prevents a safe implementation decision, identify it clearly. Continue with work that does not depend on that answer. Never invent credentials, routes, source identifiers, field names, authorization rules, or backend mappings.

## Authoritative references

Read these before changing code:

1. `AIRspec.md` — normative behavior.
2. `schema/` — JSON Schema validation layer.
3. `IMPLEMENTATION.md` — Host architecture, validation checklist, Data Broker contract, and definition of done.
4. `conformance/manifest.json` and its fixtures.
5. `schema/1.0/catalog.schema.json` and the project's Source Catalog.
6. For Class AV or AVI, the contract, fixtures, and package documentation in `https://github.com/bzalk/airmark-engine`.

When code, examples, and prose disagree, follow the normative AIRspec document and versioned schema. Report the discrepancy and add a regression test.

## Non-negotiable boundaries

* AIRspec documents are configuration, never code.
* Validate before storage and before rendering.
* Never evaluate document strings, including formulas, templates, callbacks, dynamic imports, property paths, or identifier-encoded expressions.
* Never accept document-provided URLs, credentials, raw SQL, raw HTML, connection strings, or inline Dataset definitions at execution time.
* All data access goes through a server-side Data Broker using server-held credentials and the current viewer's authorization.
* The report-generating AI receives the AIRspec schema and Source Catalog. It does not receive credentials or raw business data unless the Host deliberately exposes a viewer-authorized, row-capped preview tool.
* Unknown vocabulary is rejected or rendered as a safe diagnostic; it is never silently interpreted.
* Preserve existing application behavior and unrelated user changes.

## Required modules

Implement these separable responsibilities using conventions native to the project:

1. `types` — AIRspec, AIRMark, Source Catalog, policy, and structured error types.
2. `schemaValidator` — select the schema matching `document.airspec`.
3. `semanticValidator` — references, unique IDs, sources/fields, Dataset outputs, aliases, bindings, derived/calc fields, components, selections, interactions, and routes.
4. `authorizationValidator` — viewer/source/field/classification/limit policy, including derived-field classification roll-up.
5. `airmarkValidator` — closed vocabulary, output fields, URL/expression scan, and complexity limits.
6. `runtimeValidator` — parameter values, response shape, row limits, encoded fields on every row, and stale-response protection.
7. `parameterStore` and `bindingResolver` — validated state and complete typed alternatives only.
8. `datasetClient` — deduplicated requests keyed by version, Dataset, normalized parameters, pagination, and viewer scope.
9. `dataBroker` — server-side execution of stored Dataset definitions.
10. `componentRegistry` and `layoutWalker` — trusted renderers, recursive layout, visibility, and error boundaries.
11. `interactionDispatcher` — fixed event/action vocabulary and registered routes.
12. `chartAdapter` — validated AIRMark plus broker rows and exact pixels to scene graph and platform primitives.

Do not combine validation, data fetching, and drawing into one component.

## Implementation sequence

### 1. Inspect the repository

Locate entry points, router, state management, server boundary, authorization, design system, tests, and build commands. Reuse existing architecture. Record a short checklist, then implement.

### 2. Source Catalog and types

Create or validate the first Source Catalog against `schema/1.0/catalog.schema.json`. Use logical IDs and business field names—not UUIDs or endpoints. Map logical names to physical columns only inside a server source adapter. Preserve closed unions in the types.

### 3. Validation pipeline

Run every layer in order and return machine-readable errors such as:

```json
{
  "layer": 2,
  "code": "UNKNOWN_DATASET_FIELD",
  "path": "layout.children[1].graphic.encoding.y.field",
  "message": "Field 'revenue' is not produced by dataset 'sales'.",
  "suggestion": "Use declared alias 'total_revenue'."
}
```

Schema validation alone is not conformance. Implement the exhaustive Layer-2 checklist in `IMPLEMENTATION.md`, viewer authorization, AIRMark validation, and runtime checks.

### 4. Data Broker

Implement a server endpoint equivalent to:

```text
POST /api/reports/{versionId}/datasets/{datasetId}/execute
body: { parameters, page }
```

The server loads the immutable document and Dataset. The client never submits a Dataset definition.

```text
authenticate → load version → locate Dataset → authorize viewer/source/fields
→ validate parameters → resolve bindings → compile structured derivations
→ derive rows → filter → aggregate → calculated metrics → sort/limit/page
→ normalize alias-keyed rows → strip unauthorized fields → clamp → return
```

Use fixed implementations for structured arithmetic. Never concatenate document content into executable expressions. Follow null and division-by-zero semantics. Every output must use the declared alias verbatim. Add tests for derived multiply → grouped sum → calculated ratio and for rejection of an incomplete rollup row.

### 5. Host renderer

Implement trusted renderers for:

* containers: `stack`, `grid`, `section`;
* content: `heading`, `text`, `divider`;
* data: `metric`, `table`, `filterBar`, `emptyState`, `chart`;
* `visibleWhen`, responsive grid spans, gaps, titles, formatting, and safe defaults.

Every data component needs loading, empty, invalid, authorization-failure, source-failure, and success states. One component failure must not take down the report. Unknown components produce a safe diagnostic.

### 6. Charts

For JavaScript/TypeScript, prefer `@airspec/airmark-engine`. For another language, implement the AIRMark Scene Graph contract and goldens.

```text
validated graphic + alias-keyed rows + measured width/height + resolved theme
→ deterministic scene graph → thin platform renderer
```

Layout and display dimensions must be identical. Measure the real content box, call layout with those pixels, and draw at scale 1. On resize, re-run layout; do not CSS-scale a scene calculated for another size.

Render every supported scene node or reject it explicitly. Display preformatted `meta.tooltip` entries without reinterpreting them. Use selection metadata for events.

### 7. State and interactions

Resolve defaults and validate updates. Bindings select complete alternatives, never patches. Include all affecting parameters in cache keys. Coalesce refreshes and reject stale responses using revisions. Dispatch only declared actions. Resolve navigation through registered route IDs.

### 8. Generator integration

Provide the versioned schema, viewer-appropriate Source Catalog, Host limits, concise shape guidance, and valid examples. Prefer constrained structured output. Validate, return errors, and retry with a strict cap.

Prompt rules must require logical catalog IDs and aliases; structured `derived.expr` for row math; calc-form metrics for ratios; shared domains plus `scale.reverse` for mirrored pairs; and titled, formatted tooltip arrays for hover charts. Never give the generator credentials or unrestricted data tools.

## Testing requirements

* Wire `python conformance/runner.py --cmd "<validator command>"` into project tests.
* Execute broker fixtures and compare expected rows.
* Test loading, empty, errors, unknown components, visibility, and responsive layout.
* Run AIRMark fixtures/goldens or an equivalent port suite.
* Mount a chart in a wide, short cell and assert drawn bounds fit its content box.
* Test tooltip labels, formatted values, and escaping.
* Turn every defect into a fixture before fixing it.

## Definition of done

Do not declare completion until:

* full validation occurs before render and execution;
* one real Source works end-to-end through the broker;
* the first report renders metric, table, and chart components;
* parameters, visibility, bindings, empty states, and failures are exercised;
* data never bypasses viewer authorization;
* every output field is alias-keyed and every row is complete;
* charts render at scale 1 and resize by re-layout;
* conformance, broker, unit, integration, type, lint, and production-build commands pass;
* no secrets, unrelated changes, or attribution were added unless explicitly requested.

At handoff, summarize files changed, commands run, conformance results, unsupported vocabulary, and the next safest vertical slice. Do not claim support for behavior that lacks a passing test.
