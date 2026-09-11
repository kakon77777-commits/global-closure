/* Execute the JS shipped inside index.html using a deliberately small DOM double.
 * This is runtime-logic/DOM-output evidence, never a browser playtest. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const root = path.resolve(__dirname, '..');
const htmlPath = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const extract = id => {
  const match = html.match(new RegExp(`<script id="${id}"[^>]*>([\\s\\S]*?)<\\/script>`));
  assert.ok(match, `Generated HTML must embed ${id}.`);
  return match[1];
};
const levelText = extract('level-data');
const runtime = extract('game-runtime');
const level = JSON.parse(levelText);
const savedLevel = JSON.parse(fs.readFileSync(path.join(root, 'design/generated/level.json')));
const designProof = JSON.parse(fs.readFileSync(path.join(root, 'design/generated/build-evidence.json'))).proof;
const evidence = [];
function check(name, run) {
  const observation = run();
  evidence.push({name, passed: true, observation});
}

function boot(source = runtime) {
  const elements = new Map();
  for (const [, id] of html.matchAll(/\bid="([^"]+)"/g)) {
    elements.set(id, {
      id, style: {}, dataset: {}, hidden: false, textContent: '', listeners: {}, attributes: {},
      setAttribute(name, value) { this.attributes[name] = value; },
      addEventListener(event, listener) { this.listeners[event] = listener; }
    });
  }
  elements.get('level-data').textContent = levelText;
  const listeners = {};
  const document = {
    getElementById(id) {
      assert.ok(elements.has(id), `Runtime looked up missing DOM id ${id}`);
      return elements.get(id);
    },
    addEventListener(event, listener) { listeners[event] = listener; }
  };
  const window = {};
  vm.runInNewContext(source, {document, window}, {filename: 'index.html#game-runtime'});
  function key(key, options = {}) {
    let prevented = false;
    listeners.keydown({key, repeat: false, altKey: false, ctrlKey: false, metaKey: false,
      target: {tagName: 'BODY'}, preventDefault() { prevented = true; }, ...options});
    return prevented;
  }
  const state = () => JSON.parse(JSON.stringify(window.keyDoor.snapshot()));
  return {elements, key, state, restart() { elements.get('restart').listeners.click(); }};
}
const keys = {up:'ArrowUp', down:'ArrowDown', left:'ArrowLeft', right:'ArrowRight'};

check('generated_level_is_exact_saved_design_data', () => {
  assert.deepEqual(level, savedLevel);
  return {path:'design/generated/level.json', player:level.player, key:level.key, exit:level.exit};
});
check('all_five_actual_svg_assets_are_embedded_and_used', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'art/generated/manifest.json')));
  const result = {};
  for (const [id, relative] of Object.entries(manifest.assets)) {
    const bytes = fs.readFileSync(path.join(root, relative));
    const uri = `data:image/svg+xml;base64,${bytes.toString('base64')}`;
    assert.ok(html.includes(`data-asset="${id}"`), `${id} must be used in markup.`);
    assert.ok(html.includes(`src="${uri}"`), `${id} must embed its exact produced bytes.`);
    result[id] = crypto.createHash('sha256').update(bytes).digest('hex');
  }
  assert.ok(html.indexOf('id="player"') > html.indexOf('id="exit"'), 'Player must layer after exit.');
  assert.ok(!/<(?:script|link)[^>]*(?:src|href)\s*=/.test(html), 'No external scripts or stylesheets.');
  assert.ok(!/\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(/.test(runtime), 'No network runtime APIs.');
  return result;
});
check('boot_exposes_initial_position_key_and_objective', () => {
  const game = boot();
  assert.deepEqual(game.state(), {position:[0,0], hasKey:false, won:false, moves:0, event:'ready'});
  assert.match(game.elements.get('inventory').textContent, /not found/i);
  assert.match(game.elements.get('objective').textContent, /find.*key/i);
  assert.equal(game.elements.get('key').hidden, false);
  return game.state();
});
function checkLockedDoor(game) {
  const trace = [];
  for (const direction of ['up','right','down','right','right','right']) {
    assert.equal(game.key(keys[direction]), true);
    trace.push(game.state());
  }
  assert.deepEqual(trace.map(state => state.event),
    ['blocked_bounds','moved','blocked_wall','moved','moved','blocked_exit']);
  assert.deepEqual(game.state().position, [3,0]);
  assert.equal(game.state().moves, 3);
  assert.equal(game.state().hasKey, false);
  assert.equal(game.state().won, false);
  assert.match(game.elements.get('feedback').textContent, /locked/i);
  return trace;
}
check('shipped_keyboard_handler_blocks_bounds_walls_and_locked_exit', () => checkLockedDoor(boot()));
check('design_solution_collects_key_on_move_8_and_wins_on_move_16', () => {
  const game = boot();
  const trace = [];
  for (const [i, direction] of designProof.actions.entries()) {
    game.key(keys[direction]);
    trace.push(game.state());
    if (i < 15) assert.equal(game.state().won, false);
    if (i === 7) {
      assert.equal(game.state().hasKey, true);
      assert.equal(game.elements.get('key').hidden, true);
      assert.match(game.elements.get('inventory').textContent, /collected/i);
      assert.match(game.elements.get('objective').textContent, /door/i);
    }
  }
  assert.deepEqual(game.state(), {position:level.exit, hasKey:true, won:true, moves:16, event:'won'});
  assert.equal(game.elements.get('board').dataset.state, 'won');
  assert.match(game.elements.get('objective').textContent, /made it out/i);
  assert.equal(game.elements.get('player').style.left, '80%');
  assert.equal(game.elements.get('player').style.top, '0%');
  const won = game.state();
  game.key('ArrowLeft');
  assert.deepEqual(game.state(), won, 'Winning state remains stable until restart.');
  game.restart();
  assert.deepEqual(game.state(), {position:level.player, hasKey:false, won:false, moves:0, event:'ready'});
  assert.equal(game.elements.get('key').hidden, false);
  assert.match(game.elements.get('inventory').textContent, /not found/i);
  return {trace, restart:game.state()};
});
check('wasd_uppercase_restart_repeat_and_unrelated_keys', () => {
  const game = boot();
  game.key('s'); game.key('D'); game.key('S'); game.key('W'); game.key('A'); game.key('w');
  assert.deepEqual(game.state().position, [0,0]);
  game.key('d', {repeat:true});
  assert.deepEqual(game.state().position, [0,0], 'Holding a key does not create a second action.');
  assert.equal(game.key('x'), false);
  assert.equal(game.key('d', {ctrlKey:true}), false);
  game.key('d'); game.key('R');
  assert.deepEqual(game.state(), {position:level.player, hasKey:false, won:false, moves:0, event:'ready'});
  return game.state();
});
check('locked_exit_witness_rejects_a_removed_lock_guard', () => {
  const guard = 'if (same(next, level.exit) && !state.hasKey)';
  assert.ok(runtime.includes(guard), 'Named mutation must reach the implemented guard.');
  const badRuntime = runtime.replace(guard, 'if (false)');
  let rejected = false;
  try { checkLockedDoor(boot(badRuntime)); } catch (error) {
    if (error.code === 'ERR_ASSERTION') rejected = true;
    else throw error;
  }
  assert.equal(rejected, true, 'Locked-exit witness must reject the known wrong runtime.');
  return 'The same keyboard replay rejects a runtime whose locked-door condition was disabled.';
});

const report = {
  schema:1, passed:true, consumer:'Node vm executing index.html#game-runtime with a minimal DOM double',
  input:path.relative(root, htmlPath),
  input_sha256:crypto.createHash('sha256').update(html).digest('hex'),
  witness_sha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex'),
  checks:evidence,
  boundary:'Actual shipped JavaScript, keyboard/click callbacks and DOM assignments ran. No browser engine, image decode, layout, focus, screen-reader or human playtest was exercised.'
};
fs.mkdirSync(path.join(root, 'programming/generated'), {recursive:true});
fs.writeFileSync(path.join(root, 'programming/generated/runtime-evidence.json'), JSON.stringify(report, null, 2)+'\n');
console.log(`${evidence.length}/${evidence.length} runtime checks passed; browser playtest: not performed.`);
