# Adapters

AIRMark is a grammar, not a library — it prescribes no rendering technology. This directory is reserved for **reference adapter sketches**: worked examples of translating a validated AIRMark `graphic` object into the configuration format of popular chart runtimes.

Planned sketches:

* `airmark-to-vega-lite/` — mark/encoding translation for Vega-Lite runtimes
* `airmark-to-echarts/` — series/option translation for Apache ECharts
* `airmark-to-chartjs/` — dataset/option translation for Chart.js

## Adapter rules of the road

An adapter is an invisible Host implementation detail. To stay conformant it must:

1. Accept only **validated** AIRMark input (Layers 1–4 already passed).
2. Inject data exclusively from the Host's Data Broker as the `airspecData` datasource — never let the target library load data itself.
3. Strip or refuse any target-library capability prohibited by AIRspec.md §10.2 and §15 (URLs, expressions, external resources), even if the target library supports it.
4. Apply the resolution order from §10.1: Host security overrides → tenant theme → document theme → graphic properties → renderer defaults.

Contributions welcome — an adapter sketch should include a short README, a translation table (AIRMark concept → target concept), and one worked example using `samples/class-av-dashboard.json`.
