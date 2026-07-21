# AI Coding Prompt: Implement AIRspec in React

Copy everything below the divider into your AI coding tool. Fill in the Project Brief first.

---

You are implementing a production-ready AIRspec Host renderer inside an existing React application. Work directly in the supplied repository. Use its established router, state, styling, server, authentication, testing, and error-reporting patterns rather than creating a parallel application.

## Project Brief

```yaml
project_name: "FILL IN"
react_stack: "React version, router, build system, SSR/CSR"
language: "TypeScript preferred; describe current setup"
package_manager: "FILL IN"
styling_and_design_system: "FILL IN"
server_runtime: "FILL IN"
database_or_data_apis: "FILL IN"
authentication_and_authorization: "FILL IN"
existing_routes: "FILL IN"
target_conformance_class: "A, AV, or AVI"
first_source_to_implement: "FILL IN"
first_report_to_render: "FILL IN"
test_typecheck_lint_build_commands: "FILL IN"
```

If required business information is missing, state the blocker precisely and continue with independent work. Never invent credentials, source IDs, field mappings, permissions, or routes.

## Read before coding

1. `AIRspec.md`
2. `schema/`
3. `IMPLEMENTATION.md`
4. `conformance/`
5. the project's Source Catalog
6. `https://github.com/bzalk/airmark-engine`
7. non-normative working reference: `https://github.com/JamrockPartners/airspec-demo`

The demo is an architectural example, not the conformance authority. Follow the current AIRspec repository and schemas when they differ. Do not copy fixed chart dimensions: use measured content boxes through `AirmarkChartAuto` or an equivalent `ResizeObserver` integration.

## Install and verify packages

For Class AV/AVI:

```bash
npm install @airspec/airmark-engine @airspec/airmark-react @airspec/airmark-svg
```

Use the project's package manager equivalent when it is not npm. Confirm resolved versions and exported types before writing wrappers. Do not vendor `dist/` unless explicitly required.

## Security and data boundary

* AIRspec documents are untrusted declarative configuration.
* Run schema, semantic, authorization, AIRMark, and runtime checks before drawing.
* Never use `eval`, `Function`, `dangerouslySetInnerHTML`, expression parsers, document callbacks, dynamic imports, raw queries, or document URLs.
* React components never fetch arbitrary document addresses.
* The browser sends only immutable version ID, Dataset ID, validated parameters, and pagination to the Data Broker.
* The Broker loads the stored Dataset and applies the current viewer's permissions using server-held credentials.
* The report-generating AI receives schema and Source Catalog structure—not credentials or raw application data.

## Required React structure

Adapt names to the existing project while keeping responsibilities separate:

```text
airspec/
  types.ts
  validation/
    schema.ts
    semantic.ts
    authorization.ts
    airmark.ts
    runtime.ts
  state/
    ReportProvider.tsx
    parameters.ts
    bindings.ts
    interactions.ts
  data/
    datasetClient.ts
    cacheKey.ts
  renderer/
    ReportRenderer.tsx
    LayoutWalker.tsx
    componentRegistry.ts
    ComponentBoundary.tsx
    components/
      AirStack.tsx
      AirGrid.tsx
      AirSection.tsx
      AirHeading.tsx
      AirText.tsx
      AirDivider.tsx
      AirMetric.tsx
      AirTable.tsx
      AirFilterBar.tsx
      AirEmptyState.tsx
      AirChart.tsx
server/
  dataBroker/
    executeDataset.ts
    sourceAdapters/
```

Reuse established project folders if equivalents exist. Do not duplicate the router, authentication, query cache, formatting, or UI primitives.

## Build sequence

### 1. Inspect the application

Locate the report route, authenticated server boundary, API client, state/query library, design system, error boundaries, and tests. Identify reusable patterns, then implement rather than only describing them.

### 2. Types and Source Catalog

Model closed AIRspec unions without weakening everything to untyped records. Keep an escape hatch only for `x-` extensions. Validate the Source Catalog against `schema/1.0/catalog.schema.json`; physical backend mappings stay server-side.

### 3. Validation pipeline

Expose a pure API such as:

```ts
type ValidationError = {
  layer: 1 | 2 | 3 | 4 | 5;
  code: string;
  path: string;
  message: string;
  suggestion?: string;
};

validateDocument(document, catalog, policy): ValidationError[];
```

Use Draft 2020-12 JSON Schema for Layer 1. Implement every semantic check in `IMPLEMENTATION.md`, including aliases, stable outputs, bindings, derived/calc fields, components, interactions, routes, and selections. TypeScript types do not replace runtime validation.

### 4. Server-side Data Broker

Implement the broker before connecting components to real data. The client calls a stored Dataset by immutable version and ID; it never submits the Dataset body.

```text
authenticate → load version → find Dataset → authorize → validate parameters
→ resolve bindings → structured derivations → filters → aggregation → calc metrics
→ sort/limit/page → alias-keyed rows → authorization strip → response clamp
```

Use source adapters for logical-to-physical mappings. Structured arithmetic uses fixed operators and catalog mappings, never generated code or string-built SQL. Test derived multiply → grouped sum → calculated ratio. Reject incomplete aggregate/rollup rows.

### 5. Report state

Implement `ReportProvider` or integrate with existing state. It owns immutable document identity, parameters/defaults, resolved bindings, Dataset states, deduplication/cache keys, selections, atomic interactions, state revisions, and stale-response rejection.

Avoid one state variable per component and request effects that loop. Prefer normalized report state and pure resolvers.

### 6. Registry and layout walker

Use a trusted registry:

```ts
const componentRegistry = {
  stack: AirStack,
  grid: AirGrid,
  section: AirSection,
  heading: AirHeading,
  text: AirText,
  divider: AirDivider,
  metric: AirMetric,
  table: AirTable,
  filterBar: AirFilterBar,
  emptyState: AirEmptyState,
  chart: AirChart,
} satisfies Record<SupportedComponentType, React.ComponentType<AirComponentProps>>;
```

`LayoutWalker` evaluates `visibleWhen`, looks up the trusted component, and renders a safe diagnostic for unknown types. Containers recurse through the walker. Wrap data components in error boundaries so one failure cannot remove the report.

Implement the responsive 12-column grid from component properties. Styling belongs to trusted components; document strings never become class names, CSS, or HTML.

### 7. Data components

Metric and table components consume broker rows, AIRspec formatting, and trusted theme primitives. Render loading, empty, error, authorization, invalid, and success states. Multiple components using one Dataset must share one execution.

Filter controls update declared parameters only and validate values before dispatch. Server validation remains authoritative.

### 8. React chart integration

Use `AirmarkChartAuto` inside report grid cells:

```tsx
<AirmarkChartAuto
  graphic={validatedGraphic}
  rows={brokerRows}
  theme={resolvedTheme}
  selectionState={selectionState}
  transitionMs={prefersReducedMotion ? undefined : 250}
  onSelect={handleSelect}
/>
```

Requirements:

* The card/grid determines the available box.
* `AirmarkChartAuto` measures that box and re-lays-out on resize.
* Do not use a hardcoded `height: 360px` unless the Host deliberately resolved that exact height.
* Do not stretch a differently sized SVG with `width: 100%`.
* Give the container a meaningful minimum height and `overflow: hidden` as a safety net.
* Respect `prefers-reduced-motion`; `transitionMs` is optional presentation.
* Use engine-generated `meta.tooltip`; native `<title>` works automatically and styled overlays may read the same entries without reformatting.
* Selection callbacks dispatch declared interactions only.

For server export, pass the same deterministic scene graph to `@airspec/airmark-svg`.

### 9. Interactions

Support only declared events/actions. Apply multi-action changes atomically, resolve dependencies once, and refresh each affected Dataset at most once per revision. Resolve navigation through the application's route registry; never construct URLs from report content.

### 10. Generator integration

Give the model the schema, viewer-appropriate Source Catalog, Host limits, concise vocabulary guidance, and valid examples. Prefer constrained output. Validate, return machine-readable errors, and retry with a strict cap.

Prompt rules require real catalog fields and logical sources; stable aliases; structured `derived.expr`; calc metrics for ratios; shared domains with `scale.reverse` for mirrored pairs; and titled, formatted tooltip arrays for hover charts. Never expose credentials or unrestricted data tools.

## Required tests

1. Run the AIRspec conformance runner against the validator.
2. Execute broker fixtures against the real adapter boundary.
3. Test schema-invalid, semantic-invalid, unauthorized, and AIRMark-invalid documents.
4. Test every trusted component's loading/empty/error/success states.
5. Test unknown components and component error boundaries.
6. Test parameters, visibility, bindings, atomic actions, deduplication, and stale responses.
7. Mount a span-12 chart in a wide, short cell and assert the SVG stays inside it.
8. Test native tooltip text, formatting, and escaping.
9. Test reduced motion and prove transitions do not change scene output.
10. Run tests, type checking, lint, and production build.

Every defect discovered becomes a regression fixture.

## Definition of done

Do not report completion until:

* validation precedes storage, render, and execution;
* one real Source and report work end-to-end;
* the browser cannot submit or modify Dataset definitions;
* output rows are complete and keyed by declared aliases;
* one failed component degrades locally;
* chart layout and display pixels match at tested sizes;
* viewer authorization is enforced at validation and execution;
* conformance, broker, React, type, lint, and production-build checks pass;
* unsupported vocabulary throws or displays a precise diagnostic;
* no unrelated changes, credentials, secrets, or attribution were added unless explicitly requested.

At handoff, provide files changed, architectural decisions, exact commands/results, supported class, unsupported features, and the next recommended fixture. Do not claim behavior without a passing test.
