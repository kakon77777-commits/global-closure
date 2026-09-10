import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { mergeBatches } from '../record_merge.mjs';

const fixturePath = fileURLToPath(new URL('../examples/research-batches.json', import.meta.url));
const cliPath = fileURLToPath(new URL('../record_merge.mjs', import.meta.url));
const input = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const result = mergeBatches(input);

test('all twelve input rows retain provenance or a rejection', () => {
  assert.equal(result.summary.received, 12);
  assert.equal(result.summary.accepted_rows, 11);
  assert.equal(result.rejected.length, 1);
  const variants = result.resolved.concat(result.conflicts.flatMap(c => c.variants));
  assert.equal(variants.reduce((n, row) => n + row.sources.length, 0), 11);
});
test('schema aliases and fullwidth identifiers normalize together', () => {
  const row = result.resolved.find(r => r.id === 'P-002');
  assert.equal(row.status, 'draft');
  assert.deepEqual(row.sources, ['A:2', 'B:2']);
});
test('duplicate records keep both sources', () => {
  assert.equal(result.summary.duplicate_extra_rows, 2);
  assert.deepEqual(result.resolved.find(r => r.id === 'P-001').sources, ['A:1', 'B:1']);
});
test('conflicts keep each version without inflating completion', () => {
  assert.equal(result.conflicts[0].id, 'P-004');
  assert.deepEqual(result.conflicts[0].variants.map(v => v.status).sort(), ['done', 'in_progress']);
  assert.equal(result.resolved.some(r => r.id === 'P-004'), false);
  assert.equal(result.summary.statuses.done, 3);
});
test('same title with different identifiers is not merged', () => {
  assert.deepEqual(result.summary.repeated_titles, [{title: '注意力算子', ids: ['P-001', 'P-006']}]);
});
test('invalid records retain original fields and source', () => {
  assert.equal(result.rejected[0].source, 'C:3');
  assert.deepEqual(result.rejected[0].errors, ['invalid_id']);
  assert.equal(result.rejected[0].original.標題, '待命名草稿');
});
test('unknown statuses cannot become valid records', () => {
  const r = mergeBatches([{source: 'X', rows: [{id: 'P-009', title: 'T', series: 'S', status: 'unknown'}]}]);
  assert.equal(r.summary.resolved_ids, 0);
  assert.deepEqual(r.rejected[0].errors, ['unknown_status']);
});
test('series and status totals reconcile', () => {
  assert.equal(result.summary.unique_ids, 8);
  assert.equal(result.summary.resolved_ids, 7);
  assert.deepEqual(result.summary.statuses, {done: 3, draft: 2, in_progress: 2});
  assert.equal(result.summary.by_series.reduce((n, row) => n + row.total, 0), 7);
});
test('input is not mutated or aliased into rejected output', () => {
  const copied = structuredClone(input);
  const before = JSON.stringify(copied);
  const output = mergeBatches(copied);
  output.rejected[0].original.標題 = 'changed';
  assert.equal(JSON.stringify(copied), before);
});
test('empty input and repeated execution are stable', () => {
  assert.equal(mergeBatches([]).summary.received, 0);
  assert.deepEqual(mergeBatches(input), result);
});
test('conflict-only series are retained with zero valid records', () => {
  assert.deepEqual(result.summary.by_series.find(r => r.series === '記憶'), {
    series: '記憶', total: 0, done: 0, draft: 0, in_progress: 0, conflict_ids: 1,
  });
});
test('all five accepted series appear without inflating valid totals', () => {
  assert.equal(result.summary.by_series.length, 5);
  assert.equal(result.summary.by_series.reduce((n, row) => n + row.conflict_ids, 0), 1);
});
test('a cross-series conflict counts once per affected series', () => {
  const r = mergeBatches([{source: 'T', rows: [
    {id: 'P-010', title: 'A', series: '甲', status: 'done'},
    {id: 'P-010', title: 'A', series: '甲', status: 'draft'},
    {id: 'P-010', title: 'A', series: '乙', status: 'done'},
  ]}]);
  assert.equal(r.summary.conflict_ids, 1);
  assert.equal(r.summary.resolved_ids, 0);
  assert.equal(r.summary.by_series.length, 2);
  assert.ok(r.summary.by_series.every(row => row.conflict_ids === 1 && row.total === 0));
});
test('malformed batches and ambiguous provenance are rejected clearly', () => {
  assert.throws(() => mergeBatches({}), /array of batches/);
  assert.throws(() => mergeBatches([{source: 'X'}]), /rows array/);
  assert.throws(() => mergeBatches([{source: 'X', rows: []}, {source: ' X ', rows: []}]), /unique/);
  const r = mergeBatches([{source: 'X', rows: [null, 'invalid']}]);
  assert.equal(r.rejected.length, 2);
});
test('real CLI writes a report with exit 1 and preserves source bytes', t => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'closure '));
  t.after(() => fs.rmSync(directory, {recursive: true, force: true}));
  const source = path.join(directory, '中文 source.json');
  const output = path.join(directory, 'results', 'merged.json');
  const bytes = fs.readFileSync(fixturePath);
  fs.writeFileSync(source, bytes);
  const run = spawnSync(process.execPath, [cliPath, source, '--output', output], {encoding: 'utf8', cwd: directory});
  assert.equal(run.status, 1, run.stderr);
  assert.deepEqual(JSON.parse(fs.readFileSync(output, 'utf8')), result);
  assert.deepEqual(fs.readFileSync(source), bytes);
});
test('CLI rejects source overwrite and reports malformed JSON', t => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'closure '));
  t.after(() => fs.rmSync(directory, {recursive: true, force: true}));
  const source = path.join(directory, 'source.json');
  fs.writeFileSync(source, '[]');
  const run = spawnSync(process.execPath, [cliPath, source, '--output', source], {encoding: 'utf8'});
  assert.equal(run.status, 2);
  assert.equal(fs.readFileSync(source, 'utf8'), '[]');
  fs.writeFileSync(source, '{invalid');
  const bad = spawnSync(process.execPath, [cliPath, source, '--output', path.join(directory, 'out.json')], {encoding: 'utf8'});
  assert.equal(bad.status, 2);
  assert.match(bad.stderr, /ERROR:/);
});
