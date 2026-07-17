# AIRspec

**AI Reporting Specification** — a declarative, safety-first JSON format for AI-generated dynamic reports.

> The AI generates the report *definition*. Your application renders it with trusted code. Nothing the AI produces is ever executed.

AIRspec defines a portable JSON document that describes a complete interactive report — parameters, data requirements, layout, components, charts, theming, and interactions. Charts are expressed in **AIRMark**, AIRspec's built-in mark-and-encoding grammar, which has no data-loading surface, no URLs, and no expression evaluation by design.

📄 **Read the full specification: [AIRspec.md](./AIRspec.md)**

---

## Why AIRspec exists

Letting an AI model generate reports is powerful. Letting an AI model generate *code* that runs in your application is dangerous. AIRspec resolves that tension with one rule:

**The AI produces configuration. Your app owns all execution.**

An AIRspec document cannot call an API, reference a URL, embed a credential, run a formula, or inject HTML — those capabilities are structurally absent from the format, not merely discouraged. Your application interprets the document with trusted components, fetches data through your own authenticated data broker, and enforces authorization on every request.

```text
User request (natural language)
        ↓
AI Generator  ──→  AIRspec Document (validated JSON)
                          ↓
              Your trusted renderer + data broker
                          ↓
                 Live, interactive report
```

---

## How to Use

You don't need to read any code to get oriented. There are two roles in every AIRspec system — the **Host** (your application) and the **Generator** (your AI pipeline) — and you can adopt each incrementally.

### Step 1 — Decide what your Host will support

The spec defines three conformance classes so you can start small:

| Class | What it includes | Good for |
| --- | --- | --- |
| **A — Core** | Layout, text, metrics, tables, filters, datasets | A first working version with no charting at all |
| **AV — Visualization** | Class A + the AIRMark chart grammar | Full dashboards |
| **AVI — Interactive** | Class AV + cross-component interactions (drilldowns, exports) | Production analytics experiences |

### Step 2 — Choose how you'll render charts (Class AV+)

AIRMark is a *grammar*, not a library. It has **zero dependencies** and prescribes no rendering technology. You have three practical options, all equally conformant:

1. **Translate to a chart library you already use.**
   Write a small internal adapter that converts a validated AIRMark `graphic` object into the configuration format of Vega-Lite, ECharts, Chart.js, Highcharts, Plotly, or similar. This is usually the fastest path — AIRMark's mark/encoding shape maps naturally onto most modern chart libraries. The adapter is an invisible implementation detail; your stored documents remain pure AIRspec.

2. **Build a bespoke renderer.**
   Render AIRMark directly to SVG or Canvas. Most control, most effort. Sensible if you already have an in-house charting system or unusual visual requirements.

3. **Skip charts initially.**
   Ship Class A (metrics, tables, filters, layout) first. Add AIRMark support later without changing any document you've already stored — documents are forward-compatible.

Whichever you choose, the observable behavior must match §10 of the spec, and the security rules in §15 always apply.

### Step 3 — Build the Host foundations

In rough order of construction:

1. **Publish a Source Catalog** — describe your data sources, fields, and capabilities as logical business concepts using the [Source Catalog schema](./schema/1.0/catalog.schema.json) (spec §6). This is the only view of your data the AI ever sees.
2. **Implement the Data Broker** — one trusted server endpoint that executes stored dataset definitions with the *viewer's* authorization and server-held credentials (§7.7, §18-adjacent).
3. **Implement validation** — JSON Schema first, then semantic, authorization, and AIRMark checks (§14). Return machine-readable errors so the AI can self-correct.
4. **Implement the renderer** — map each component type to one of your trusted UI components (§8–§9).

### Step 4 — Wire up the Generator

Any model or provider works. The pattern:

1. Give the model the AIRspec JSON Schema, your Source Catalog, and your limits as context.
2. Use structured/constrained output so the model emits a single JSON document.
3. Validate. On failure, feed the machine-readable errors back and let the model retry.
4. Store the passing document as an **immutable version**. Render it. Regeneration creates a new version; old versions remain restorable.

### Just evaluating?

Read §2 (Design Principles) and §18 (Complete Example Document) of [AIRspec.md](./AIRspec.md) — together they take about ten minutes and show you the entire model.

---

## Repository layout

```text
AIRspec.md          The specification (start here)
IMPLEMENTATION.md   Build guide for implementing an AIRspec Host
README.md           This file
LICENSE             MIT
schema/
  1.0/
    airspec.schema.json Published JSON Schema (Validation Layer 1)
    catalog.schema.json Published Source Catalog JSON Schema
conformance/        Conformance fixtures, manifest, policy, and runner
samples/
  class-a-table-report.json             Class A: tables + metrics, no charts
  class-av-dashboard.json               Class AV: adds an AIRMark chart
  class-avi-interactive-dashboard.json  Class AVI: selections, drilldown,
                                        navigation, export
  catalogs/orders.catalog.json          Example Source Catalog entry
adapters/           Reference adapter sketches for popular chart
                    runtimes (sketches planned — see adapters/README.md)
```

Every sample validates against the published schema — see `samples/README.md` for a one-liner to try it yourself. Contributions welcome.

---

## Design principles (the short version)

1. **Configuration, not code** — no document content is ever executed.
2. **Logical data access only** — sources and fields by name, never URLs or credentials.
3. **Deny by default** — anything not allowlisted is rejected.
4. **Immutability** — published documents are versions; changes create new versions.
5. **Fail soft** — one broken component never takes down the report.

---

## Relationship to other standards

AIRspec and AIRMark are self-contained: conformance is measured against [AIRspec.md](./AIRspec.md) alone, and no external grammar, schema, or runtime is required. The grammar-of-graphics tradition — notably [Vega-Lite](https://vega.github.io/vega-lite/) — served as a valuable design reference, and translating AIRMark to such runtimes is a perfectly valid way to implement a Host.

---

## License

MIT (recommended; see [LICENSE](./LICENSE)).

---

*AIRspec — declare the report, trust the host.*
