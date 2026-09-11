# Cross-conversation handoff

Use the project's existing durable state and transport when suitable. The optional Python helper below is a portable file protocol, not a chat service, scheduler, identity verifier, or Git client.

## One world, three role entries

Keep one compact authoritative record containing the project/repository locator, scope, target platform/engine, current revision, active contracts, current integration owner and known blockers. Keep role-local work and incoming/outgoing packets separate. Reuse existing filenames and schemas; do not duplicate an established tracker.

Record each actual context locator and its available state when observed. A role name does not prove that another agent is running. With only one context, work sequentially and label peer review unavailable; leave handoffs for real later contexts.

For a new conversation, supply the project locator, role, pinned revision and pending packet location. It reads the current shared state, relevant contract and addressed packet; it does not need the full prior chat. If its project copy is stale, synchronize the necessary revision before treating an artifact as missing.

## Exchange the smallest useful projection

A handoff carries: source/recipient role, observed context locator or explicit unknown, base revision, changed artifact references, evidence and its limits, unresolved decisions, and the next required action. Reference evidence files rather than embedding long logs. Never include credentials or private conversation dumps.

Use `DELIVER` for a candidate contribution, `REQUEST` for a specific dependency, and a receiver-produced `ACK` or `CHALLENGE` referencing the packet ID. An ACK states what was actually inspected or integrated and at which revision; receipt, technical acceptance and product acceptance remain distinct. Do not forge another role's ACK. Native context messages may point to a durable packet, but message delivery alone is not artifact acceptance.

Each role writes only its assigned files, role workspace and new packets. Use isolated branches/worktrees or non-overlapping paths; the integration owner applies cross-role changes to the shared baseline. Read the current remote head before an authorized Git publication; preserve other writers' changes and use a normal fast-forward/update with conflict detection. Do not force-push to erase a conflict. A change to a shared contract is an explicit proposal until integrated.

When a packet is stale, compare the changed contract and affected outputs. Rebase or regenerate only what the new evidence invalidates. Do not relabel old evidence as fresh or restart unrelated work. Preserve earlier packets and supersede them with a new packet.

Cross-conversation work is asynchronous unless a real transport and runtime provide live delivery. Do not poll idle conversations or create a background service by default. If no shared storage is available, prepare a portable project snapshot and entry instruction, and describe delivery as pending.

## Optional local helper

[studio_handoff.py](../scripts/studio_handoff.py) requires Python 3.10+ and only its standard library. It creates JSON packets and checks exact world, contract and artifact bytes. It makes no network calls, sends no messages, runs no packet-supplied commands and changes no shared project state. Its hashes check snapshot integrity, not authorship, authority, gameplay correctness or independent review.

To use it, create a small world JSON in your project (default `studio/world.json`, configurable with `--world`). These fields are the helper's format only:

```json
{
  "schema": 1,
  "project_id": "my-game",
  "revision": 1,
  "scope": "Complete the agreed first playable level",
  "target": "The selected engine and target platform",
  "integrator": "programming",
  "contracts": ["studio/asset-contract.json", "studio/gameplay-contract.json"]
}
```

Every listed contract must exist. Keep volatile chat status outside this snapshot so ordinary messages do not invalidate game contracts. Only the current integration owner advances the baseline revision after integrating a relevant change.

Write a short UTF-8 note with the contribution, actual checks, unresolved items and next action. Select only the produced artifact and evidence files needed by the recipient. Copy the helper into the project's existing tools area if useful, or invoke it at its discovered skill path. For the following PowerShell examples, `$handoffTool` is that actual path:

```powershell
py -3 $handoffTool pack --project . --from-role design --to-role programming --context 'actual-context-locator' --note .\design-handoff.md --artifact 'design/generated-level.json' --artifact 'design/evidence.json' --output .\design-delivery.json
py -3 $handoffTool verify --project . --packet .\design-delivery.json --as-role programming
```

Artifact paths use project-relative forward slashes. Packet files reference artifacts; transfer the referenced project files through the shared repository or authorized file transport as well. The helper will not overwrite an existing packet. Its output is a local file until the sender saves it through that transport.

The recipient checks freshness, then reads and exercises the contribution as required. It can create an ACK packet with `--kind ACK --reply-to <received-packet-id>` and its own context locator and note. Verification returns `CURRENT` only for matching local bytes, never automatic approval. Errors return exit code 2; successful packing or freshness checking returns 0.
