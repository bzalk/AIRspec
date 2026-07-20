# AIRspec Conformance Suite

Fixture documents that define what a conforming AIRspec implementation must accept and must reject. If your validation pipeline gets every case in `manifest.json` right, you can trust it — without reading its code. That is the point: this suite is how you verify an implementation you didn't write, including one written by an AI agent.

## Contents

```text
manifest.json          Every case: file, expectation, violation layer, reason
catalog.json           The Source Catalog all fixtures validate against
policy.example.json    Example Layer-3 authorization policy for the L3 cases
runner.py              Reference runner (see below)
valid/                 Documents that MUST be accepted across supported
                       AIRspec versions and conformance classes
invalid/               Documents that MUST be rejected, spanning all
                       four validation layers
broker/                Data Broker execution fixtures with input and expected alias-keyed rows
```

## Semantics

* **`accept`** — a conforming pipeline MUST accept the document, given `catalog.json` and `policy.example.json` as context.
* **`reject`** — a conforming pipeline MUST reject the document **no later than** the declared layer. Rejecting earlier is conformant: the published Layer-1 schema is deny-by-default, so it structurally catches several Layer-4 (AIRMark) violations before an AIRMark validator ever sees them.
* Layer-2 and Layer-3 cases are **deliberately schema-valid**. They pass Layer 1 so that they genuinely exercise your semantic and authorization validators — a pipeline that only runs JSON Schema will wrongly accept them.

The runner reads each document's `airspec` value and selects the corresponding versioned schema. AIRspec 1.0 fixtures remain checked against `schema/1.0`; AIRspec 1.1 reactive-binding and structured-derived-field fixtures are checked against `schema/1.1`.

Layers (AIRspec.md §14): **1** Schema · **2** Semantic · **3** Authorization · **4** AIRMark.

## Running

```bash
pip install jsonschema

# Layer-1 verification of the whole suite (also proves the fixtures
# themselves are correctly constructed):
python conformance/runner.py

# Full-pipeline verification against YOUR validator. Your command is
# invoked per case as `<cmd> <document> <catalog> <policy>` and must
# exit 0 to accept, non-zero to reject:
python conformance/runner.py --cmd "node ./dist/validate.js"
python conformance/runner.py --cmd "python -m myapp.airspec_validate"
```

The runner exits 0 when all verifiable expectations hold, 1 otherwise — wire it into CI so every change to your validator (or to the fixtures) is checked automatically.

Broker fixtures are runtime contracts rather than validator cases, so `runner.py` does not execute them. Feed each fixture's `dataset` and `inputRows` through the source adapter/broker pipeline and deep-compare its returned rows with `expectedRows`.

## Layer 3 is policy-shaped

Authorization is Host-defined by design, so the two L3 cases are written against `policy.example.json` (a denied field classification and a row-limit ceiling). When testing your own implementation, either implement that example policy shape in your test harness or substitute an equivalent policy of your own that denies the same two things. The conformance requirement is only that documents violating the active policy are rejected.

## Adding cases

New fixtures are welcome and cheap: add the document under `valid/` or `invalid/`, add a manifest entry with the expectation and (for rejects) the layer and one-line violation, and run `runner.py` to prove the fixture behaves as declared. Good candidates are any bug you find in a real implementation — turn the bug's input into a fixture so no implementation regresses on it again.
