# AIRspec Samples

Example AIRspec documents, one per conformance class, plus an example Source Catalog.

| File | Class | Demonstrates |
| --- | --- | --- |
| `class-a-table-report.json` | **A — Core** | Parameters, aggregate + list datasets, metrics, a table with badges and conditional styling, an empty state. No charts. |
| `class-av-dashboard.json` | **AV — Visualization** | Everything in Class A plus an AIRMark line chart with a temporal axis, color encoding, tooltips, and format objects. |
| `class-avi-interactive-dashboard.json` | **AVI — Interactive** | Everything in Class AV plus selections, a layered dual-axis chart, chart-to-parameter drilldown, row-click navigation to a registered route, and CSV export. |
| `catalogs/orders.catalog.json` | — | An example Source Catalog entry: the logical data description a Host publishes to the Generator (illustrative — catalog shape is Host-defined). |

## Validating a sample

Every sample validates against `../schema/airspec.schema.json` (Validation Layer 1). For example, with Python:

```bash
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schema/airspec.schema.json'))
doc = json.load(open('samples/class-av-dashboard.json'))
jsonschema.validate(doc, schema)
print('valid')
"
```

Remember that schema validation is only Layer 1. A real Host must also run semantic, authorization, AIRMark, and runtime validation (AIRspec.md §14) — for example, verifying that `orders` actually exists in *your* catalog and that every referenced field is real.
