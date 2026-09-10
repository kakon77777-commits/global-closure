# Default-page repair evidence

Working directory: `/workspace/scratch/7a888c34f410/lspr-cases/query-default`.
Runtime: `python --version` returned `Python 3.12.14`.

## Responsibility and replacement boundary

`CONTRACT.md` requires missing/null limits to default to **2**, while `total`
remains **3**. The CLI, adapter, domain, and document store already implement
that behavior. The incorrect expectation belongs to the **test layer**.

The replacement boundary is the item-count assertion in
`QueryTests.test_default_page`: change expected length from `3` to `2`.
The existing total assertion and explicit-limit test remain intact. Production
files and the contract are unchanged; `DocumentStore` continues to own its rows.

Changed files: `test_query.py` and this evidence record. No installation or
publication was performed.

## Before replacement

Executed against the unchanged test and implementation:

```sh
python --version && python -m unittest -v test_query.QueryTests.test_default_page
```

Exit code **1**; `AssertionError: 2 != 3` at
`self.assertEqual(len(result["items"]), 3)`.
The input was `{}`; the authoritative expected page size was 2, the observed
page size was 2, and the test incorrectly demanded 3.

```sh
printf '%s\n' '{}' | python query_cli.py
```

Exit code **0**, with this contract-conforming reply:

```json
{"items": [{"id": "a", "title": "Alpha"}, {"id": "b", "title": "Beta"}], "total": 3, "limit": 2}
```

## After replacement and replay

```sh
python -m unittest -v test_query
```

Exit code **0**; both `test_default_page` (the original failing witness) and
`test_explicit_limit` passed: `Ran 2 tests`, `OK`.

The following command was also executed successfully. It exercises the actual
CLI subprocess through adapter, domain, and store, and checks repeated queries
against one shared store for mutation:

```sh
python - <<'PY'
import json
import subprocess
import sys

from query_adapter import decode_query
from query_domain import query_page
from query_store import DocumentStore

cases = [
    ({}, 2),
    ({"limit": None}, 2),
    ({"limit": "0"}, 0),
    ({"limit": "1"}, 1),
    ({"limit": "4"}, 4),
    ({"limit": "100"}, 100),
    ({"limit": "-1"}, None),
    ({"limit": "101"}, None),
]
store = DocumentStore()
before = store.read_page(100)
for query, expected_limit in cases:
    completed = subprocess.run(
        [sys.executable, "query_cli.py"],
        input=json.dumps(query), text=True, capture_output=True,
    )
    if expected_limit is None:
        assert completed.returncode == 2, (query, completed)
        assert completed.stdout == "", (query, completed.stdout)
        print(f"CLI {json.dumps(query)} -> exit 2")
    else:
        assert completed.returncode == 0, (query, completed)
        result = json.loads(completed.stdout)
        expected = {"items": before[:expected_limit], "total": 3, "limit": expected_limit}
        assert result == expected, (query, result, expected)
        assert query_page(store, decode_query(query)) == expected
        print(f"CLI {json.dumps(query)} -> items={len(result['items'])}, total=3, limit={expected_limit}")
    assert store.read_page(100) == before
    assert store.count() == 3
print("PASS: 8 CLI cases; shared store unchanged")
PY
```

Observed: missing/null limits returned 2 items; zero returned no items; explicit
1 returned one item; 4 and 100 returned all 3 items; -1 and 101 exited with code
2. Valid replies preserved the expected limit and total of 3. The final line
was `PASS: 8 CLI cases; shared store unchanged` (process exit code **0**).

Local witness, adjacent behavior, and the real CLI boundary are closed.
No remaining blocker was found within this repair boundary.
