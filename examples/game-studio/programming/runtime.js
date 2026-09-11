(() => {
  'use strict';
  const level = JSON.parse(document.getElementById('level-data').textContent);
  const ui = Object.fromEntries(['board', 'player', 'key', 'inventory', 'objective',
    'feedback', 'moves', 'restart'].map(id => [id, document.getElementById(id)]));
  const walls = new Set(level.walls.map(cell => cell.join(',')));
  const vectors = {up:[0,-1], down:[0,1], left:[-1,0], right:[1,0]};
  const inputs = {arrowup:'up', w:'up', arrowdown:'down', s:'down',
    arrowleft:'left', a:'left', arrowright:'right', d:'right'};
  const same = (a, b) => a[0] === b[0] && a[1] === b[1];
  let state;

  function render() {
    ui.player.style.left = `${state.position[0] / level.width * 100}%`;
    ui.player.style.top = `${state.position[1] / level.height * 100}%`;
    ui.key.hidden = state.hasKey;
    ui.inventory.textContent = state.hasKey ? 'Key: collected' : 'Key: not found';
    ui.moves.textContent = `${state.moves} ${state.moves === 1 ? 'move' : 'moves'}`;
    ui.objective.textContent = state.won ? 'You made it out!' : state.hasKey
      ? 'The door is ready. Head for the exit.' : 'Find the brass key, then enter the door.';
    ui.board.dataset.state = state.won ? 'won' : state.hasKey ? 'unlocked' : 'locked';
    ui.board.setAttribute('aria-label', `${level.width} by ${level.height} room. ` +
      `Player at column ${state.position[0] + 1}, row ${state.position[1] + 1}. ` +
      `${state.hasKey ? 'Key collected.' : 'Key not collected.'} ${state.won ? 'You won.' : ''}`);
    const feedback = {
      ready:'A little room, a little adventure.',
      moved:state.hasKey ? 'Carry the key to the arched door.' : 'Explore the open stone tiles.',
      blocked_bounds:'The edge of the room stops you.',
      blocked_wall:'A stone wall blocks the way.',
      blocked_exit:'The door is locked. Find the brass key.',
      key_collected:'Key collected! The door is now unlocked.',
      won:`Room cleared in ${state.moves} moves. Play again whenever you like.`
    };
    ui.feedback.textContent = feedback[state.event];
  }

  function restart() {
    state = {position:[...level.player], hasKey:false, won:false, moves:0, event:'ready'};
    render();
  }

  function move(direction) {
    if (state.won) return;
    const [dx, dy] = vectors[direction];
    const next = [state.position[0] + dx, state.position[1] + dy];
    if (next[0] < 0 || next[0] >= level.width || next[1] < 0 || next[1] >= level.height) {
      state.event = 'blocked_bounds';
    } else if (walls.has(next.join(','))) {
      state.event = 'blocked_wall';
    } else if (same(next, level.exit) && !state.hasKey) {
      state.event = 'blocked_exit';
    } else {
      state.position = next;
      state.moves += 1;
      state.event = 'moved';
      if (same(next, level.key) && !state.hasKey) {
        state.hasKey = true;
        state.event = 'key_collected';
      }
      if (same(next, level.exit) && state.hasKey) {
        state.won = true;
        state.event = 'won';
      }
    }
    render();
  }

  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (['INPUT','TEXTAREA','SELECT'].includes(event.target?.tagName) || event.target?.isContentEditable) return;
    const key = event.key.toLowerCase();
    const direction = inputs[key];
    if (!direction && key !== 'r') return;
    event.preventDefault();
    if (event.repeat) return;
    if (key === 'r') restart();
    else move(direction);
  });
  ui.restart.addEventListener('click', restart);
  // A read-only snapshot supports bounded diagnostics without changing gameplay.
  window.keyDoor = Object.freeze({snapshot:() => ({...state, position:[...state.position]})});
  restart();
})();
