# Working on Global Closure

This is an executable software MVP: a Python document inventory and a Node.js record merger. Preserve both tools, their source-preserving behavior, example inputs, and documented CLI exit codes.

For substantial in-scope development, use [global-first-completion](skills/global-first-completion/SKILL.md). Implement the whole requested path before concentrated verification. The skill guides execution; the user's requested software remains the deliverable.

- Keep runtime dependencies in the standard libraries unless the requested feature warrants another dependency.
- Keep user-facing local instructions Windows/PowerShell-first.
- Check the actual requested outputs as well as test status. In particular, conflict-only series must remain visible with zero resolved records.
- If an environment blocks the original deliverable, preserve its state and report the block. A supplementary example does not complete that original deliverable.
- Relevant checks: `python -m unittest discover -s tests -v`, `python -m compileall -q research_inventory run.py`, and `node --test tests/test_merge_records.mjs`.
- Publishing, merging, or deploying still requires applicable user authorization. Loading this skill grants none by itself.
