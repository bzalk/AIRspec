# Building a Framework-Agnostic AIRMark Renderer

Status: non-normative implementation guidance

This guide describes a portable architecture for implementing AIRMark without coupling layout logic to React, another UI framework, the DOM, SVG, Canvas, or a specific chart runtime. Conformance remains defined exclusively by `AIRspec.md`; the interfaces below are Host implementation details.

## Architecture

Split the renderer into two layers:

```text
validated AIRMark graphic + broker rows + resolved theme
                         │
                         ▼
                pure layout engine
                         │
                         ▼
              scene graph (plain data)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   React/SVG         Canvas/Web       server/native
     adapter           adapter           adapter
```

The layout engine owns every decision about data transformation, scales, axes, geometry, layering, labels, and interaction metadata. Platform adapters only draw the scene graph and translate platform events into AIRspec selection events.

## 1. Pure layout engine

A practical project structure is:

```text
src/lib/airmark-engine/
  index.ts
  types.ts
  transforms/
  scales/
  layout/
  marks/
  scene/
```

The engine accepts only inputs that have already passed AIRspec validation Layers 1–4:

```ts
export interface LayoutInput {
  graphic: AIRMarkGraphic;
  rows: ReadonlyArray<Record<string, unknown>>;
  width: number;
  height: number;
  theme: ResolvedAIRMarkTheme;
}

export interface LayoutResult {
  width: number;
  height: number;
  nodes: SceneNode[];
  warnings: LayoutWarning[];
}

export function layoutGraphic(input: LayoutInput): LayoutResult;
```

The engine MUST NOT import React, access `window` or `document`, create DOM or SVG nodes, fetch data, resolve URLs, execute expressions, or hold credentials. It should run unchanged in browsers, Node, Deno, web workers, test runners, and server-side export processes.

The engine owns:

* orientation and channel resolution;
* transform execution;
* domain computation and scale construction;
* tick generation and formatting;
* bar, point, line, area, arc, rule, text, and composite-mark geometry;
* layer and facet coordination;
* clipping, padding, label placement, and truncation;
* AIRMark sort resolution;
* selection hit metadata;
* deterministic warning generation.

## 2. Transform pipeline

Keep transforms independent of layout:

```ts
export function applyTransforms(
  rows: ReadonlyArray<Record<string, unknown>>,
  transforms: readonly AIRMarkTransform[],
): ReadonlyArray<Record<string, unknown>>;
```

Implement only the transforms allowlisted by AIRspec §10.4:

* `aggregate`
* `bin`
* `timeUnit`
* `stack`
* `window`
* `fold`
* `flatten`
* `pivot`
* structured `filter`

Each transform should be a pure function with deterministic output. Never pass a string to an expression evaluator or delegate an AIRMark transform to a target runtime that can interpret code. The transform pipeline operates only on rows injected by the trusted Host; it never loads data.

Dataset aggregation performed by the Data Broker and presentational AIRMark `aggregate` transforms are different stages. The engine implements only the latter.

## 3. Scales and axes

Move scale and axis behavior into engine utilities:

```text
computeDomain
niceBounds
niceTicks
formatTick
createLinearScale
createBandScale
createPointScale
createTemporalScale
createLogScale
createSqrtScale
```

The engine should produce positioned axis data rather than SVG elements:

```ts
interface AxisLayout {
  orient: "top" | "bottom" | "left" | "right";
  ticks: Array<{
    value: unknown;
    position: number;
    label: string;
  }>;
  title?: string;
  domainLine: LineNode;
  gridLines: LineNode[];
}
```

Linear and band scales are straightforward to implement locally. Temporal, logarithmic, and square-root behavior can optionally use `d3-scale` behind an adapter:

```ts
export interface ScaleFactory {
  create(spec: ResolvedScaleSpec, domain: unknown[], range: number[]): Scale;
}
```

The default factory can remain dependency-free. An optional factory may delegate difficult scale mathematics to `d3-scale`. That dependency remains an internal Host choice and does not change the AIRMark document or conformance rules.

## 4. Scene graph contract

The scene graph is the boundary between coordinate decisions and drawing. It is not part of AIRspec and MUST NOT be serialized into an AIRspec document.

```ts
interface SceneNodeBase {
  id: string;
  opacity?: number;
  clipId?: string;
  interaction?: InteractionMetadata;
  datum?: Readonly<Record<string, unknown>>;
  ariaLabel?: string;
}

interface RectNode extends SceneNodeBase {
  type: "rect";
  x: number;
  y: number;
  width: number;
  height: number;
  fill?: string;
  stroke?: string;
  rx?: number;
}

interface CircleNode extends SceneNodeBase {
  type: "circle";
  cx: number;
  cy: number;
  r: number;
  fill?: string;
  stroke?: string;
}

interface LineNode extends SceneNodeBase {
  type: "line";
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stroke?: string;
  strokeWidth?: number;
  dash?: number[];
}

interface PathNode extends SceneNodeBase {
  type: "path";
  commands: PathCommand[];
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
}

interface TextNode extends SceneNodeBase {
  type: "text";
  x: number;
  y: number;
  content: string;
  anchor?: "start" | "middle" | "end";
  baseline?: "top" | "middle" | "bottom" | "alphabetic";
  fontSize?: number;
  fill?: string;
  rotation?: number;
}

interface GroupNode extends SceneNodeBase {
  type: "group";
  x?: number;
  y?: number;
  children: SceneNode[];
}

type SceneNode = RectNode | CircleNode | LineNode | PathNode | TextNode | GroupNode;
```

Use numeric coordinates and structured path commands rather than prebuilt SVG strings where practical. Structured geometry is easier to validate, test, and translate to Canvas or native drawing APIs.

Interaction metadata should identify AIRMark selections without embedding callbacks:

```ts
interface InteractionMetadata {
  selectionId: string;
  event: "click" | "mouseover";
  fields: Record<string, unknown>;
}
```

Platform adapters convert user input into the fixed AIRspec selection event shape. The engine never receives arbitrary callback code.

## 5. Thin React/SVG adapter

Once the scene graph exists, a React renderer should be small:

```tsx
export function RenderGraphic(props: RenderGraphicProps) {
  const scene = useMemo(
    () => layoutGraphic(props),
    [props.graphic, props.rows, props.width, props.height, props.theme],
  );

  return (
    <svg width={scene.width} height={scene.height} role="img">
      {scene.nodes.map(node => renderSceneNode(node, props.onSelection))}
    </svg>
  );
}
```

The adapter is responsible only for:

* walking `SceneNode` values;
* emitting trusted JSX/SVG elements;
* applying clipping and accessibility attributes;
* mapping platform events from node metadata to the Host interaction dispatcher;
* reporting adapter failures through the component-level error boundary.

It does not compute domains, ticks, transforms, positions, colors, sorting, or aggregation.

The same contract supports a Svelte component, a `document.createElementNS` loop, a Canvas painter, a server-side SVG serializer, or a native-mobile drawing adapter.

## 6. Testing strategy

Test the engine rather than framework markup. Each fixture contains:

```text
AIRMark graphic
+ input rows
+ viewport and resolved theme
→ expected scene graph or geometric assertions
```

Recommended coverage:

* every mark type and orientation;
* empty, single-row, negative, zero, null, and mixed-sign data;
* grouped and stacked bars;
* layered and faceted graphics;
* quantitative, nominal, ordinal, temporal, log, and square-root scales;
* explicit and inferred domains;
* tick density, formatting, truncation, and axis titles;
* every allowlisted transform;
* AIRMark encoding sorts and row ordering produced by resolved AIRspec 1.1 Dataset bindings;
* selection metadata and overlapping hit targets;
* deterministic output for identical inputs;
* complexity limits and graceful warnings.

Prefer semantic and geometric assertions over full snapshots:

```ts
expect(rects).toHaveLength(4);
expect(rects.map(node => node.x)).toEqual([40, 90, 140, 190]);
expect(rects.every(node => node.height >= 0)).toBe(true);
expect(scene.nodes).not.toContainUnsafeValues();
```

Small focused snapshots remain useful for composite marks and axes, but avoid coupling all tests to node ordering or irrelevant defaults.

Keep a thin adapter test layer for accessibility attributes, event translation, and representative node-to-element mappings. Browser tests should not be required to verify coordinate mathematics.

## 7. Incremental migration

This architecture does not require a rewrite:

1. Define `SceneNode` and the engine input/output contract.
2. Extract bar-transform, scale, and coordinate logic first.
3. Make the existing bar component draw the returned scene nodes.
4. Add engine-level bar fixtures and compare visual output with the existing renderer.
5. Move line, area, point, rule, text, and arc marks one at a time.
6. Extract shared axes, legends, facets, layers, and transforms as duplication becomes visible.
7. Reduce the framework component to a scene-graph walker.
8. Add another adapter only after the scene graph has proven stable.

At every step, validated AIRMark input and observable output remain unchanged.

## Adoption checklist

* [ ] Layers 1–4 validation completes before the engine runs.
* [ ] Data comes only from the trusted Data Broker.
* [ ] Engine modules have no framework, DOM, network, or credential access.
* [ ] Only AIRMark-allowlisted transforms are implemented.
* [ ] Scale dependencies are behind an internal adapter.
* [ ] Scene nodes contain data and metadata, never executable callbacks or markup strings.
* [ ] Theme resolution follows AIRspec §10.1 before layout.
* [ ] Security and accessibility overrides win over document preferences.
* [ ] Geometry is covered by engine-level fixtures.
* [ ] Framework adapters contain no layout or transform decisions.

The result is a renderer whose difficult behavior is portable, deterministic, and testable without a browser, while each output platform remains a small replaceable adapter.
