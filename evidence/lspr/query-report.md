# Zero-limit investigation

Result: the alleged defect is not reproduced in the available implementation.
No correction or replacement boundary is justified. Responsibility layer: none
established; the suspected adapter transformation uses the default only for
`None`, preserving both numeric `0` and decimal-string `"0"`. The domain passes
that limit to persistence, whose zero slice is empty. The public CLI returns
`{"items": [], "total": 3, "limit": 0}` for both zero inputs.

Only this record was added. `CONTRACT.md`, all four implementation files, and
`test_query.py` remain unchanged. No installation or publication was performed.

Observed against the unchanged implementation with Python 3.12.14:

| Input | Exit | Items | Total | Reply limit |
| --- | ---: | ---: | ---: | ---: |
| Missing limit | 0 | 2 | 3 | 2 |
| `null` | 0 | 2 | 3 | 2 |
| `0` | 0 | 0 | 3 | 0 |
| `"0"` | 0 | 0 | 3 | 0 |
| `"1"` | 0 | 1 | 3 | 1 |
| `3` | 0 | 3 | 3 | 3 |
| `4` | 0 | 3 | 3 | 4 |
| `100` | 0 | 3 | 3 | 100 |
| `-1` | 2 | — | — | — |
| `101` | 2 | — | — | — |

Both rejected cases had empty stdout and stderr `limit must be between 0 and
100`. Repeated domain queries at limits 0, 1, 100, and 0 preserved all three
stored documents and their order. Existing unittest result: 2 tests, OK. No
before/after repair comparison applies because the original witnesses passed.

Replay the following commands from this project directory. Expected values use
`CONTRACT.md`; document contents and order are preserved neighboring behavior.
The investigation also read the requested LSPR skill and the seven existing
project files using `cat` and enumerated project files with `rg --files --hidden
-g '!node_modules' -g '!.git'`.

```bash
python -m unittest -v
python - <<'PY'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from query_adapter import decode_query
from query_domain import query_page
from query_store import DocumentStore

print(sys.version.splitlines()[0])
for name in ('query_cli.py', 'query_adapter.py', 'query_domain.py', 'query_store.py'):
    print(name, hashlib.sha256(Path(name).read_bytes()).hexdigest())

rows = [
    {'id': 'a', 'title': 'Alpha'},
    {'id': 'b', 'title': 'Beta'},
    {'id': 'c', 'title': 'Gamma'},
]
for label, request, expected_limit in [
    ('missing', {}, 2),
    ('null', {'limit': None}, 2),
    ('numeric zero', {'limit': 0}, 0),
    ('decimal-string zero', {'limit': '0'}, 0),
    ('neighbor', {'limit': '1'}, 1),
    ('store size', {'limit': 3}, 3),
    ('above store size', {'limit': 4}, 4),
    ('upper bound', {'limit': 100}, 100),
    ('below lower bound', {'limit': -1}, None),
    ('above upper bound', {'limit': 101}, None),
]:
    result = subprocess.run(
        [sys.executable, 'query_cli.py'], input=json.dumps(request),
        text=True, capture_output=True, check=False,
    )
    if expected_limit is None:
        assert result.returncode == 2, (label, result.returncode, result.stdout, result.stderr)
    else:
        assert result.returncode == 0, (label, result.returncode, result.stderr)
        expected = {'items': rows[:expected_limit], 'total': 3, 'limit': expected_limit}
        assert json.loads(result.stdout) == expected, (label, result.stdout, expected)
    print(f'{label}: exit={result.returncode}; stdout={result.stdout.strip()!r}; stderr={result.stderr.strip()!r}')

for raw in (0, '0'):
    assert decode_query({'limit': raw}) == {'limit': 0}
store = DocumentStore()
for limit in (0, 1, 100, 0):
    assert query_page(store, {'limit': limit}) == {
        'items': rows[:limit], 'total': 3, 'limit': limit,
    }
    assert store.read_page(100) == rows
    assert store.count() == 3
print('Boundary checks: adapter preserves zero; repeated domain/store queries preserve all 3 documents.')
print('PASS: 10 CLI contract cases and boundary checks; alleged zero-limit defect not reproduced.')
PY
```

Recorded SHA-256 fingerprints:

```text
query_cli.py 99ebb593ca1b770ec3a07b121b818d5b2aa0652ee85a2753dd5d49faff3e433e
query_adapter.py cc08a41b979463681ef58a34cc335411214d71019a2ac8c2a2b1dbdd1c6e0826
query_domain.py 2150ad3b2f2d8b22de26bce50f756cb5ac75e6b35f5c77899541894c499d5307
query_store.py ca4c302ab570121e4b6012ad7ade9be9033e30bc6b7fea9898752fc21c84b847
```

Closure is bounded to the reported zero-limit behavior and the listed contract
neighbors in this local implementation; there was no failing witness to repair
and no blocker in those checks.
