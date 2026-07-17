#!/usr/bin/env python3
"""AIRspec conformance runner.

Runs the fixture suite in manifest.json against the published AIRspec JSON
Schema (Validation Layer 1) and reports, per case, whether the Layer-1 result
is consistent with the manifest's expectation.

What this runner proves on its own:
  * Every `accept` case passes the schema.
  * Every `reject` case declared at layer 1 fails the schema.
  * Every `reject` case declared at layers 2-3 PASSES the schema (they are
    structurally valid by design, so they genuinely exercise your semantic
    and authorization validators).
  * Layer-4 cases may fail the schema early (deny-by-default) or pass it;
    either way your AIRMark validator must reject whatever the schema lets
    through.

What it cannot prove: layers 2-4 themselves. Wire in your own validator via
--cmd, which is invoked as `<cmd> <document> <catalog> <policy>` per case and
must exit 0 to accept, non-zero to reject. With --cmd supplied, the runner
verifies the full expectation for every case.

Usage:
  pip install jsonschema
  python conformance/runner.py                    # Layer-1 verification only
  python conformance/runner.py --cmd "node validate.js"   # full pipeline

Exit code 0 when all verifiable expectations hold; 1 otherwise.
"""
import argparse
import json
import pathlib
import shlex
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA_CANDIDATES = [
    HERE.parent / "schema" / "1.0" / "airspec.schema.json",
    HERE.parent / "schema" / "airspec.schema.json",
]


def load_schema():
    for p in SCHEMA_CANDIDATES:
        if p.exists():
            return json.loads(p.read_text()), p
    sys.exit("error: airspec.schema.json not found next to conformance/ "
             f"(looked in: {', '.join(str(p) for p in SCHEMA_CANDIDATES)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cmd", help="host validator command; called with "
                                  "<document> <catalog> <policy>, exit 0=accept")
    args = ap.parse_args()

    try:
        import jsonschema
    except ImportError:
        sys.exit("error: pip install jsonschema")

    schema, schema_path = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    manifest = json.loads((HERE / "manifest.json").read_text())
    catalog = HERE / manifest["catalog"]
    policy = HERE / manifest["policy"]

    print(f"schema:  {schema_path}")
    print(f"catalog: {catalog}")
    print(f"policy:  {policy}")
    print(f"cases:   {len(manifest['cases'])}\n")

    failures, pending = [], []

    for case in manifest["cases"]:
        cid, expect = case["id"], case["expect"]
        layer = case.get("layer")
        doc_path = HERE / case["file"]
        doc = json.loads(doc_path.read_text())

        schema_ok = not list(validator.iter_errors(doc))

        status, note = "ok", ""
        if expect == "accept":
            if not schema_ok:
                status, note = "FAIL", "accept case failed Layer-1 schema"
        else:  # reject
            if layer == 1 and schema_ok:
                status, note = "FAIL", "layer-1 case passed the schema"
            elif layer in (2, 3) and not schema_ok:
                status, note = "FAIL", f"layer-{layer} case failed the schema (should be structurally valid)"
            elif layer in (2, 3) and schema_ok:
                note = f"passes L1 as designed -> your layer-{layer} validator must reject it"
            elif layer == 4:
                note = ("rejected at L1 (deny-by-default)" if not schema_ok
                        else "passes L1 -> your AIRMark validator must reject it")

        if args.cmd and status == "ok":
            r = subprocess.run(
                shlex.split(args.cmd) + [str(doc_path), str(catalog), str(policy)],
                capture_output=True, text=True)
            accepted = (r.returncode == 0)
            if expect == "accept" and not accepted:
                status, note = "FAIL", f"host validator rejected an accept case: {r.stderr.strip()[:200]}"
            elif expect == "reject" and accepted:
                status, note = "FAIL", "host validator accepted a reject case"
            else:
                note = "verified by host validator"
        elif not args.cmd and expect == "reject" and layer in (2, 3, 4) and schema_ok and status == "ok":
            pending.append(cid)

        if status == "FAIL":
            failures.append(cid)
        marker = "x" if status == "FAIL" else "."
        print(f"[{marker}] {cid:<6} {expect:<7} L{layer or '-'}  {note}")

    print()
    if failures:
        print(f"FAILURES ({len(failures)}): {', '.join(failures)}")
        sys.exit(1)
    if pending:
        print(f"Layer-1 checks passed. {len(pending)} case(s) await your host "
              f"validator (rerun with --cmd): {', '.join(pending)}")
    else:
        print("All verifiable expectations hold.")


if __name__ == "__main__":
    main()
