(() => {
const map = document.getElementById('map');
const player = document.getElementById('player');
const popup = document.getElementById('popup');
const popupTitle = document.getElementById('popupTitle');
const popupBody = document.getElementById('popupBody');
const popupClose = document.getElementById('popupClose');
const victory = document.getElementById('victory');
const victoryClose = document.getElementById('victoryClose');
const xpEl = document.getElementById('xp');
const rankEl = document.getElementById('rank');
const invEl = document.getElementById('inventory');
const questsEl = document.getElementById('quests');
const energyBar = document.getElementById('energyBar');
const energyText = document.getElementById('energyText');
const locations = Array.from(document.querySelectorAll('.location'));
const hint = document.getElementById('hint');
const interactPrompt = document.getElementById('interactPrompt');
const toastsEl = document.getElementById('toasts');
const dpad = document.getElementById('dpad');

const state = {
  x: 100,
  y: 470,
  speed: 3,
  keys: {},
  energy: 80,
  xp: 0,
  inventory: new Set(),
  quests: { firstClass: false, studentId: false, libraryVisit: false, timetable: false, eatMeal: false, chooseSchool: false, programOrientation: false, completeProgramCourses: false, chooseDepartment: false, completeDepartmentCourses: false },
  flags: { dormKey: false, firstClassBadge: false, libraryCard: false, mealCoupon: false, studentId: false, timetable: false, ateMeal: false, dormStudyDone: false },
  meta: { school: null, department: null, coursesDone: 0, courses: {}, programCourses: {}, booksRead: 0 },
  currentOverlap: null,
  popupOpen: false,
  suppressUntilExit: false,
  victoryAwarded: false
};

let focusedEl = null;
let hintHidden = false;

window.GameState = state;

function showToast(message) {
  if (!toastsEl) return;
  const div = document.createElement('div');
  div.className = 'toast';
  div.textContent = message;
  toastsEl.appendChild(div);
  setTimeout(() => {
    div.style.opacity = '0';
    div.style.transform = 'translateY(6px)';
    setTimeout(() => div.remove(), 250);
  }, 1400);
}

function hideHint() {
  if (hintHidden) return;
  hintHidden = true;
  if (hint) hint.style.display = 'none';
}

function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

function updatePlayer() {
  player.style.transform = `translate3d(${state.x}px, ${state.y}px, 0)`;
}

function updateHUD() {
  xpEl.textContent = state.xp.toString();
  rankEl.textContent = rankForXP(state.xp);
  energyText.textContent = String(Math.round(state.energy));
  energyBar.style.width = `${clamp(state.energy, 0, 100)}%`;
  invEl.innerHTML = '';
  Array.from(state.inventory).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    invEl.appendChild(li);
  });
  Object.entries(state.quests).forEach(([key, done]) => {
    const li = questsEl.querySelector(`li[data-quest="${key}"]`);
    if (li) li.classList.toggle('done', !!done);
  });
}

function rankForXP(x) {
  if (x >= 100) return 'Master';
  if (x >= 60) return 'Achiever';
  if (x >= 30) return 'Explorer';
  return 'Rookie';
}

function addXP(n) {
  state.xp += n;
  showToast(`+${n} XP`);
  updateHUD();
}

function addItem(name) {
  state.inventory.add(name);
  showToast(`Item: ${name}`);
  updateHUD();
}

function completeQuest(id) {
  if (!state.quests[id]) {
    state.quests[id] = true;
    updateHUD();
    checkVictory();
  }
}

function setEnergy(v) {
  state.energy = clamp(v, 0, 100);
  updateHUD();
}

function showPopup(title, bodyBuilder) {
  popupTitle.textContent = title;
  popupBody.innerHTML = '';
  bodyBuilder(popupBody);
  popup.classList.remove('hidden');
  state.popupOpen = true;
  hideInteractPrompt();
}

function hidePopup() {
  popup.classList.add('hidden');
  state.popupOpen = false;
  state.suppressUntilExit = true;
}

popupClose.addEventListener('click', hidePopup);

function openLocationPopup(key) {
  const helpers = {
    addXP,
    addItem,
    completeQuest,
    setEnergy,
    state
  };
  const UI = window.UI || {};
  if (key === 'dorm' && typeof UI.dorm === 'function') {
    showPopup('Dormitory', body => UI.dorm(body, state, helpers));
    return;
  }
  if (key === 'classroom' && typeof UI.classroom === 'function') {
    showPopup('Classroom', body => UI.classroom(body, state, helpers));
    return;
  }
  if (key === 'library' && typeof UI.library === 'function') {
    showPopup('Library', body => UI.library(body, state, helpers));
    return;
  }
  if (key === 'cafeteria' && typeof UI.cafeteria === 'function') {
    showPopup('Cafeteria', body => UI.cafeteria(body, state, helpers));
    return;
  }
  if (key === 'admin' && typeof UI.admin === 'function') {
    showPopup('Admin Office', body => UI.admin(body, state, helpers));
    return;
  }
}

function setFocused(el) {
  if (focusedEl && focusedEl !== el) focusedEl.classList.remove('focused');
  focusedEl = el || null;
  if (focusedEl) focusedEl.classList.add('focused');
}

function showInteractPrompt() {
  if (!interactPrompt) return;
  const mapRect = map.getBoundingClientRect();
  const pRect = player.getBoundingClientRect();
  const cx = pRect.left - mapRect.left + pRect.width / 2;
  const cy = pRect.top - mapRect.top;
  interactPrompt.style.left = `${cx}px`;
  interactPrompt.style.top = `${cy}px`;
  interactPrompt.style.transform = 'translate(-50%, -120%)';
  interactPrompt.classList.remove('hidden');
}

function hideInteractPrompt() {
  if (!interactPrompt) return;
  interactPrompt.classList.add('hidden');
}

function rectsIntersect(a, b) {
  return !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
}

function checkOverlap() {
  const playerRect = player.getBoundingClientRect();
  let overlap = null;
  for (const el of locations) {
    const r = el.getBoundingClientRect();
    if (rectsIntersect(playerRect, r)) {
      overlap = el;
      break;
    }
  }
  if (!overlap) {
    setFocused(null);
    state.currentOverlap = null;
    if (state.suppressUntilExit) state.suppressUntilExit = false;
    hideInteractPrompt();
    return;
  }
  if (state.suppressUntilExit) {
    setFocused(overlap);
    state.currentOverlap = overlap;
    hideInteractPrompt();
    return;
  }
  const changed = overlap !== state.currentOverlap;
  state.currentOverlap = overlap;
  setFocused(overlap);
  if (!state.popupOpen) {
    if (changed) {
      openLocationPopup(overlap.dataset.location);
    } else {
      showInteractPrompt();
    }
  }
}

function gameLoop() {
  let dx = 0, dy = 0;
  if (state.keys['ArrowLeft']) dx -= 1;
  if (state.keys['ArrowRight']) dx += 1;
  if (state.keys['ArrowUp']) dy -= 1;
  if (state.keys['ArrowDown']) dy += 1;
  if (dx !== 0 || dy !== 0) {
    const len = Math.hypot(dx, dy) || 1;
    const vx = (dx / len) * state.speed;
    const vy = (dy / len) * state.speed;
    const playerRect = player.getBoundingClientRect();
    const pw = playerRect.width;
    const ph = playerRect.height;
    const maxX = map.clientWidth - pw;
    const maxY = map.clientHeight - ph;
    state.x = clamp(state.x + vx, 0, maxX);
    state.y = clamp(state.y + vy, 0, maxY);
    updatePlayer();
    checkOverlap();
    hideHint();
  }
  requestAnimationFrame(gameLoop);
}

function showVictory() {
  if (state.victoryAwarded) return;
  state.victoryAwarded = true;
  addXP(100);
  victory.classList.remove('hidden');
}

function checkVictory() {
  const allDone = Object.values(state.quests).every(Boolean);
  if (allDone) showVictory();
}

victoryClose.addEventListener('click', () => {
  resetGame();
  victory.classList.add('hidden');
});

function resetGame() {
  state.x = 100;
  state.y = 470;
  state.speed = 3;
  state.keys = {};
  state.energy = 80;
  state.xp = 0;
  state.inventory = new Set();
  state.quests = { firstClass: false, studentId: false, libraryVisit: false, timetable: false, eatMeal: false, chooseSchool: false, programOrientation: false, completeProgramCourses: false, chooseDepartment: false, completeDepartmentCourses: false };
  state.flags = { dormKey: false, firstClassBadge: false, libraryCard: false, mealCoupon: false, studentId: false, timetable: false, ateMeal: false, dormStudyDone: false };
  state.meta = { school: null, department: null, coursesDone: 0, courses: {}, programCourses: {}, booksRead: 0 };
  state.currentOverlap = null;
  state.popupOpen = false;
  state.suppressUntilExit = false;
  state.victoryAwarded = false;
  updatePlayer();
  updateHUD();
  checkOverlap();
}

window.addEventListener('keydown', e => {
  if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) {
    state.keys[e.key] = true;
    e.preventDefault();
  }
  if ((e.key === 'e' || e.key === 'E' || e.code === 'KeyE') && state.currentOverlap && !state.popupOpen) {
    openLocationPopup(state.currentOverlap.dataset.location);
    e.preventDefault();
  }
  if (e.key === 'Escape' && state.popupOpen) hidePopup();
});

window.addEventListener('keyup', e => {
  if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) {
    state.keys[e.key] = false;
    e.preventDefault();
  }
});

map.addEventListener('click', e => {
  if (state.popupOpen) return;
  const el = e.target.closest('.location');
  if (el) {
    openLocationPopup(el.dataset.location);
  }
});

function bindDpad() {
  if (!dpad) return;
  const mapKey = {
    up: 'ArrowUp',
    down: 'ArrowDown',
    left: 'ArrowLeft',
    right: 'ArrowRight'
  };
  function press(dir, down) {
    const key = mapKey[dir];
    if (!key) return;
    state.keys[key] = !!down;
    if (down) hideHint();
  }
  dpad.querySelectorAll('button[data-dir]').forEach(btn => {
    const dir = btn.getAttribute('data-dir');
    btn.addEventListener('pointerdown', e => { e.preventDefault(); press(dir, true); });
    btn.addEventListener('pointerup', e => { e.preventDefault(); press(dir, false); });
    btn.addEventListener('pointerleave', e => { e.preventDefault(); press(dir, false); });
    btn.addEventListener('pointercancel', e => { e.preventDefault(); press(dir, false); });
  });
}

window.GameAPI = {
  openLocationPopup,
  hideInteractPrompt,
  showInteractPrompt,
  state
};

if (!(window.PHASER_MODE && window.Phaser)) {
  updatePlayer();
  updateHUD();
  checkOverlap();
  bindDpad();
  requestAnimationFrame(gameLoop);
} else {
  const p = document.getElementById('player');
  if (p) p.style.display = 'none';
}

})();
