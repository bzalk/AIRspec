# Build an AIRspec Renderer with an AI Coding Tool

This quick start gives an AI coding agent enough structure to implement AIRspec inside an existing application without guessing at the security boundary, document vocabulary, data contract, or rendering architecture.

Choose one copy-paste prompt:

* [Framework-agnostic implementation prompt](./prompts/IMPLEMENT-GENERIC.md) — for Vue, Svelte, Angular, vanilla JavaScript, Canvas, server-rendered SVG, native applications, other languages, or a custom renderer.
* [React implementation prompt](./prompts/IMPLEMENT-REACT.md) — for React applications using the published `@airspec/airmark-*` packages.

The prompts work with any capable AI coding tool. They do not depend on a specific model, vendor, editor, or agent runtime.

## Before pasting the prompt

Give the coding agent access to your project and these AIRspec resources:

* [`AIRspec.md`](./AIRspec.md) — normative specification.
* [`schema/`](./schema/) — versioned AIRspec and Source Catalog schemas.
* [`IMPLEMENTATION.md`](./IMPLEMENTATION.md) — detailed Host architecture and validation checklist.
* [`conformance/`](./conformance/) — accept/reject fixtures and broker execution fixtures.
* [`samples/`](./samples/) — complete example documents.
* [AIRMark Engine](https://github.com/bzalk/airmark-engine) — portable scene-graph engine, adapters, fixtures, and goldens.

Fill in the Project Brief at the top of the selected prompt:

```yaml
project_name: ""
language_and_framework: ""
package_manager: ""
server_runtime: ""
database_or_data_apis: ""
authentication_and_authorization: ""
existing_routes: ""
target_conformance_class: "A | AV | AVI"
first_source_to_implement: ""
first_report_to_render: ""
test_commands: ""
```

Do not let the agent infer source names, field names, permissions, routes, or credentials. Describe them in a Source Catalog conforming to [`schema/1.0/catalog.schema.json`](./schema/1.0/catalog.schema.json).

## Recommended first milestone

Build one complete vertical slice before broadening component coverage:

1. Load one immutable AIRspec document.
2. Validate it before storage or rendering.
3. Execute one stored Dataset through a server-side broker.
4. Return flat rows keyed exactly by declared fields and aliases.
5. Render a grid containing a metric, table, and chart.
6. Exercise one parameter and one empty/error state.
7. Turn every defect into a fixture.

## What “renderer” means here

An AIRspec renderer is more than a chart component. A conforming Host includes:

```text
AIRspec document
      │
      ▼
validation layers 1–4 ── reject invalid or unauthorized configuration
      │
      ▼
layout walker + trusted component registry
      │
      ├── parameters, visibility, bindings, interactions
      ├── metric/table/text/container components
      └── chart component ── validated AIRMark + broker rows → scene graph → pixels
                              ▲
                              │
server-side Data Broker ──────┘
```

The AI that generates a report receives the schema and Source Catalog—not credentials or business data. Dataset execution happens in the Host under the viewer's authorization.

## Working reference

[`JamrockPartners/airspec-demo`](https://github.com/JamrockPartners/airspec-demo) is a working React implementation that demonstrates a component registry, recursive layout walker, validation, report state, server-side Data Broker, AIRMark integration, and conformance fixtures.

Use it as an architectural example, not as the normative definition. Conformance is measured against this repository's specification, schemas, and fixtures. New implementations should measure the chart's real content box and lay out at those exact pixels; do not copy a fixed-height or CSS-scaled SVG integration.

## Definition of done

The implementation is not complete because a sample looks correct. It is complete when:

* the versioned JSON Schema runs before semantic validation;
* semantic, authorization, AIRMark, and runtime checks are enforced;
* no document can introduce a URL, credential, executable string, raw query, or HTML surface;
* all data access passes through a viewer-authorized server-side broker;
* broker rows use declared aliases verbatim and contain every encoded field on every row;
* unknown components and per-component failures degrade safely;
* chart layout pixels equal display pixels and resize causes re-layout, not CSS scaling;
* `python conformance/runner.py --cmd "<your validator>"` passes;
* broker execution fixtures pass;
* the project's tests, type checks, lint, and production build pass.

Keep the selected prompt in your project as an implementation contract. Every production bug should become a local regression fixture and, when generally applicable, an AIRspec or AIRMark conformance case.
