# Zero-limit repair evidence

Contract: `CONTRACT.md`, Document query contract v1 (unchanged).
Working directory: `/workspace/scratch/7a888c34f410/lspr-cases/query-zero`.
Runtime: `python --version` returned `Python 3.12.14`.

## Responsibility and replacement boundary

The adapter owns conversion from the wire value to domain options. It correctly
parsed `"0"` as integer zero, then incorrectly changed it to the default at its
return statement. Before replacement, the localization command below printed
`adapter: {'limit': 2}` and
`domain with explicit zero: {'items': [], 'total': 3, 'limit': 0}`:

```sh
python - <<'PY'
from query_adapter import decode_query
from query_domain import query_page
from query_store import DocumentStore

print("adapter:", decode_query({"limit": "0"}))
print("domain with explicit zero:", query_page(DocumentStore(), {"limit": 0}))
PY
```

The production replacement is confined to `query_adapter.py`, in `decode_query`:

```diff
-    return {"limit": limit or DEFAULT_LIMIT}
+    return {"limit": limit}
```

Missing/null defaulting, integer conversion, and range validation are unchanged.
`query_cli.py`, `query_domain.py`, `query_store.py`, and the original assertions
in `test_query.py` are unchanged. Queries retain no state in the adapter; the
document store continues to own its rows and return copies.

## Executed failing witness and its replay

The following exact command was run before and after the production edit:

```sh
python - <<'PY'
import json
import subprocess
import sys

query = '{"limit":"0"}'
expected = {"items": [], "total": 3, "limit": 0}
result = subprocess.run([sys.executable, "query_cli.py"], input=query, text=True, capture_output=True)
print("input:", query, flush=True)
print("expected:", expected, flush=True)
print("observed exit:", result.returncode, flush=True)
print("observed stdout:", result.stdout.strip(), flush=True)
print("observed stderr:", result.stderr.strip(), flush=True)
assert result.returncode == 0, result.stderr
assert json.loads(result.stdout) == expected
PY
```

- Before: CLI exit 0, empty stderr, stdout
  `{"items": [{"id": "a", "title": "Alpha"}, {"id": "b", "title": "Beta"}], "total": 3, "limit": 2}`.
  The witness exited 1 with `AssertionError` against the v1 contract.
- After: CLI exit 0, empty stderr, stdout
  `{"items": [], "total": 3, "limit": 0}`. The witness exited 0.
  This exercises stdin JSON parsing, adapter, domain, store, and stdout JSON.

## Regression and closure commands

| Command | Before production edit | After production edit |
| --- | --- | --- |
| `python -m unittest -v` | Original 2 tests passed before test additions. | All 8 tests passed; exit 0. |
| `python -m unittest -v test_query.QueryTests.test_zero_limit test_query.QueryTests.test_cli_zero_limit` | Added tests ran against unchanged production code: 2 tests, 3 failures; exit 1. Both numeric and string zero became 2, and the CLI returned two documents. | Both tests passed as part of the full 8-test run. |

Added coverage checks zero at the adapter and public handler, the real CLI zero
request, null/missing defaults, limits larger than the store through the maximum
100, negative/above-100 CLI rejection with exit 2, and unchanged stored rows/count
after zero, one, and maximum-limit queries. Existing default and explicit-one
tests remain intact. The production line shown above captures the original
behavior if a before-state replay is needed in a disposable copy.

Changed files: `query_adapter.py`, `test_query.py`, and this record. No dependencies,
contract changes, publishing, or installation were needed. Closure has no blocker.
