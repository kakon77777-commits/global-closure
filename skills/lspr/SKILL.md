---
name: lspr
description: Local Surgical Proof & Replacement for a mostly working system with one suspicious node, failure, or invariant. Find the smallest justified replacement boundary, demonstrate the defect before editing, and close local plus adjacent behavior. Use for bounded diagnosis and repair, not greenfield implementation or broad refactoring.
---

# LSPR — Local Surgical Proof & Replacement

Input: an already mostly complete system and one suspicious node, failure, or invariant. Keep this a local repair skill, not a new project workflow.

$$
\boxed{\text{Maximum Local Precision} + \text{Minimum Global Disturbance}}
$$

Here, **proof** means an executable or checkable falsifying witness against an established contract, not a claim of formal mathematical proof. The central task is **Replacement Boundary Detection**: determine what is wrong, what must change, and what must remain untouched.

$$
\boxed{\text{No Replacement Without a Failing Witness}}
$$

## 1. Minimize the problem domain

Trace only the dependencies that can cause the observed failure and the immediately affected consumers. Identify the smallest **evidence-supported sufficient** dependency cone; do not claim a mathematically minimal cone or assume one file is always sufficient.

Before editing, identify the suspect implementation, its entry/exit contracts, state ownership, and neighboring behavior to preserve. Read beyond this boundary only when evidence requires it. A small diff that patches a symptom at the wrong layer is not a small repair.

## 2. Establish the falsifying witness

Use an existing reproducer or construct the smallest case that retains the relevant causal behavior. Derive expected behavior from the user's requirement, an authoritative contract, or an independent oracle; do not invent a new requirement to make the old code fail.

**Run the witness against the unchanged implementation before replacing behavior.** Preserve its input, expected result, observed failure, and enough command/version context to replay it. A setup/import failure or an assertion that merely repeats a suspicion does not establish a defect in the target implementation.

If the alleged failure cannot be reproduced, leave implementation unchanged and report the bounded finding or missing prerequisite. Do not create a cosmetic replacement to demonstrate progress.

The sole exception is an explicitly requested, behavior-preserving mechanical edit. State the deterministic transformation and use a relevant equivalence/syntax check; do not manufacture a failing bug test. API, schema, persistence, dependency, ordering, and algorithm changes do not qualify merely because they are short.

## 3. Assign the responsibility layer

Locate the violated contract in **protocol / adapter / persistence / domain / test / environment**. Follow the first incorrect transformation or state transition, not the most visible downstream symptom.

A failing test is evidence to investigate, not permission to change production code. If the test contradicts the established contract, demonstrate that mismatch and repair the test. If the environment is responsible, address only the established prerequisite within existing authority; do not disguise it with a domain-code change. Keep unproven layers explicitly uncertain.

## 4. Replace only the necessary implementation

Change the smallest causally sufficient implementation within the identified boundary, plus the witness and directly necessary boundary tests. Preserve surrounding contracts and unrelated user changes.

Do not reformat neighbors, rename public identities, upgrade dependencies, redesign interfaces, or refactor adjacent modules as cleanup. If the witness shows that a contract or wider architecture must change, stop this local replacement path and surface that scope change. Do not force a local patch across an invalid boundary.

## 5. Close local behavior, then the boundary, then stop

Verify the same previously failing witness now passes; check the adjacent invariants affected by the replacement, including a valid neighboring case; run **one end-to-end witness through the relevant real entry point and affected boundary**. A direct unit call is not automatically end-to-end.

Reuse an existing check when it genuinely covers more than one of these obligations. Keep unchanged assertions intact unless the test itself was shown to be responsible. Run any genuinely required project gate without inventing additional gates.

Once these obligations pass, **stop**. Do not start another global review, expand the search to unrelated warnings, or seek hypothetical local perfection. If a required witness is blocked, report that unverified boundary rather than claiming closure.

Return a compact result: replacement boundary and responsibility layer; before/after witness evidence; files changed and preserved neighbors; closure checks and any remaining blocker. No mandatory report file or administrative checklist is needed.

The skill can follow Global First Completion and mssp-tdd-apr when their work identifies a local target. It also works alone: the three roles are not a mandatory three-stage pipeline, and LSPR does not automatically invoke the other skills.
