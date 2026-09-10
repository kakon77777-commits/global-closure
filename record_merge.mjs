/** Merge research records while keeping conflicts and source provenance. */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const aliases = new Map([
  ['完成', 'done'], ['done', 'done'],
  ['草稿', 'draft'], ['draft', 'draft'],
  ['進行中', 'in_progress'], ['in_progress', 'in_progress'],
]);
const clean = value => typeof value === 'string' ? value.trim() : '';
const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;

function normalize(raw, source) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return { valid: false, source, errors: ['invalid_record'], original: raw };
  }
  const id = clean(raw.id ?? raw.paper_id ?? raw.稿號).normalize('NFKC').toUpperCase();
  const title = clean(raw.title ?? raw.name ?? raw.標題);
  const series = clean(raw.series ?? raw.category ?? raw.系列);
  const status = aliases.get(clean(raw.status ?? raw.state ?? raw.狀態).normalize('NFKC').toLowerCase());
  const errors = [];
  if (!/^P-\d{3}$/.test(id)) errors.push('invalid_id');
  if (!title) errors.push('missing_title');
  if (!series) errors.push('missing_series');
  if (!status) errors.push('unknown_status');
  return errors.length
    ? { valid: false, source, errors, original: structuredClone(raw) }
    : { valid: true, document: { id, title, series, status }, source };
}

export function mergeBatches(batches) {
  if (!Array.isArray(batches)) throw new TypeError('Input must be an array of batches.');
  const batchNames = new Set();
  const normalized = [];
  for (const batch of batches) {
    if (!batch || typeof batch !== 'object' || !clean(batch.source) || !Array.isArray(batch.rows)) {
      throw new TypeError('Each batch needs a source name and a rows array.');
    }
    const name = clean(batch.source);
    if (batchNames.has(name)) throw new TypeError('Batch source names must be unique.');
    batchNames.add(name);
    batch.rows.forEach((row, index) => normalized.push(normalize(row, `${name}:${index + 1}`)));
  }

  const groups = new Map();
  const rejected = [];
  for (const item of normalized) {
    if (!item.valid) { rejected.push(item); continue; }
    const d = item.document;
    if (!groups.has(d.id)) groups.set(d.id, new Map());
    const versions = groups.get(d.id);
    const signature = JSON.stringify([d.title, d.series, d.status]);
    if (!versions.has(signature)) versions.set(signature, { ...d, sources: [] });
    versions.get(signature).sources.push(item.source);
  }
  const resolved = [];
  const conflicts = [];
  for (const id of [...groups.keys()].sort(compare)) {
    const variants = [...groups.get(id).values()];
    variants.forEach(v => v.sources.sort(compare));
    variants.sort((a, b) => compare(JSON.stringify(a), JSON.stringify(b)));
    if (variants.length === 1) resolved.push(variants[0]);
    else conflicts.push({ id, variants });
  }

  const statuses = { done: 0, draft: 0, in_progress: 0 };
  const series = new Map();
  const variants = resolved.concat(conflicts.flatMap(c => c.variants));
  // Initialize from every accepted variant, including conflict-only series.
  for (const row of variants) {
    if (!series.has(row.series)) series.set(row.series, {
      series: row.series, total: 0, done: 0, draft: 0, in_progress: 0, conflict_ids: 0,
    });
  }
  for (const conflict of conflicts) {
    for (const name of new Set(conflict.variants.map(v => v.series))) series.get(name).conflict_ids++;
  }
  const titles = new Map();
  for (const row of variants) {
    if (!titles.has(row.title)) titles.set(row.title, new Set());
    titles.get(row.title).add(row.id);
  }
  for (const row of resolved) {
    statuses[row.status]++;
    const totals = series.get(row.series);
    totals.total++;
    totals[row.status]++;
  }
  const repeatedTitles = [...titles.entries()]
    .filter(([, ids]) => ids.size > 1)
    .map(([title, ids]) => ({ title, ids: [...ids].sort(compare) }))
    .sort((a, b) => compare(a.title, b.title));
  return {
    schema_version: 1,
    summary: {
      received: normalized.length,
      accepted_rows: normalized.length - rejected.length,
      rejected_rows: rejected.length,
      unique_ids: resolved.length + conflicts.length,
      resolved_ids: resolved.length,
      conflict_ids: conflicts.length,
      duplicate_extra_rows: variants.reduce((n, row) => n + row.sources.length - 1, 0),
      statuses,
      by_series: [...series.values()].sort((a, b) => compare(a.series, b.series)),
      repeated_titles: repeatedTitles,
    },
    resolved, conflicts, rejected,
  };
}

export function main(argv = process.argv.slice(2)) {
  if (argv.length === 1 && argv[0] === '--help') {
    console.log('Usage: node record_merge.mjs INPUT.json --output OUTPUT.json');
    return 0;
  }
  try {
    if (argv.length !== 3 || argv[1] !== '--output') {
      throw new Error('Usage: node record_merge.mjs INPUT.json --output OUTPUT.json');
    }
    const input = fs.realpathSync(argv[0]);
    const output = path.resolve(argv[2]);
    if (input === output || (fs.existsSync(output) && fs.realpathSync(output) === input)) {
      throw new Error('Output must be different from the source file.');
    }
    const raw = fs.readFileSync(input, 'utf8').replace(/^\uFEFF/, '');
    const result = mergeBatches(JSON.parse(raw));
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n', 'utf8');
    const s = result.summary;
    console.log(`Report written: ${s.resolved_ids} resolved ids; ${s.conflict_ids} conflicts; ${s.rejected_rows} rejected rows.`);
    return s.conflict_ids || s.rejected_rows ? 1 : 0;
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    return 2;
  }
}

if (process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url) {
  process.exitCode = main();
}
