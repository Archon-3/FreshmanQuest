(function(){
  function createPhaserScene(){
    const mapEl = document.getElementById('map');
    if (!mapEl || !window.Phaser) return;

    const width = mapEl.clientWidth;
    const height = mapEl.clientHeight;

    const config = {
      type: Phaser.AUTO,
      width,
      height,
      parent: mapEl,
      transparent: true,
      pixelArt: true,
      physics: { default: 'arcade', arcade: { debug: false } },
      scene: { preload, create, update }
    };

    const game = new Phaser.Game(config);

    let player;
    let cursors;
    let buildings = [];
    let lastOverlapKey = null;

    function parseBuildings(){
      const els = Array.from(document.querySelectorAll('#map .location'));
      const list = els.map(el => ({
        key: el.dataset.location,
        x: el.offsetLeft,
        y: el.offsetTop,
        w: el.offsetWidth,
        h: el.offsetHeight,
        color: pickColor(el.dataset.location)
      }));
      return list;
    }

    function pickColor(k){
      switch(k){
        case 'dorm': return 0x7c3aed;
        case 'classroom': return 0x2563eb;
        case 'library': return 0xd97706;
        case 'cafeteria': return 0xdc2626;
        case 'admin': return 0x059669;
        default: return 0x64748b;
      }
    }

    function preload(){
      const g = this.make.graphics({x:0,y:0,add:false});
      // grass texture 32x32
      g.clear();
      g.fillStyle(0xeafbe7,1); g.fillRect(0,0,32,32);
      g.lineStyle(1,0xcdecc5,1); g.beginPath(); g.moveTo(0,16); g.lineTo(32,16); g.strokePath();
      g.lineStyle(1,0xdff7d7,1); g.beginPath(); g.moveTo(16,0); g.lineTo(16,32); g.strokePath();
      g.fillStyle(0xd0f0c8,1); for(let i=0;i<20;i++){ g.fillCircle(Math.random()*32, Math.random()*32, 0.7); }
      g.generateTexture('grass_tile',32,32);

      // path texture 32x32
      g.clear();
      g.fillStyle(0xf3e8d7,1); g.fillRect(0,0,32,32);
      g.lineStyle(1,0xe8dcc8,1); g.beginPath(); g.moveTo(0,16); g.lineTo(32,16); g.strokePath();
      g.lineStyle(1,0xe8dcc8,1); g.beginPath(); g.moveTo(16,0); g.lineTo(16,32); g.strokePath();
      g.generateTexture('path_tile',32,32);
      g.destroy();
    }

    function create(){
      // tile background grass
      const bg = this.add.tileSprite(0,0,width,height,'grass_tile');
      bg.setOrigin(0,0);

      // campus paths
      const paths = this.add.layer();
      function addPath(x,y,w,h){ const ts = paths.scene.add.tileSprite(x,y,w,h,'path_tile'); ts.setOrigin(0,0); paths.add(ts); }
      addPath(100, 260, 680, 40); // horizontal main
      addPath(220, 120, 40, 300); // vertical to admin/cafe
      addPath(620, 120, 40, 300); // vertical to library/cafe

      // buildings from DOM
      buildings = parseBuildings();
      buildings.forEach(b => {
        const gb = this.add.graphics();
        gb.fillStyle(b.color, 0.28);
        gb.fillRoundedRect(b.x, b.y, b.w, b.h, 12);
        gb.lineStyle(2, 0x111827, 0.18);
        gb.strokeRoundedRect(b.x, b.y, b.w, b.h, 12);
        // simple roof cap
        gb.fillStyle(0x111827, 0.06); gb.fillRect(b.x, b.y-6, b.w, 6);
        b._g = gb;
      });

      // decor trees
      const trees = this.add.graphics();
      trees.fillStyle(0x166534,1);
      for (let i=0;i<14;i++){
        const tx = Math.random()*width;
        const ty = Math.random()*height;
        if (ty > 100 && ty < height-40) trees.fillCircle(tx, ty, 6);
      }

      // player
      const start = window.GameState ? {x: window.GameState.x, y: window.GameState.y} : {x: 100, y: 470};
      player = this.add.circle(start.x + 11, start.y + 11, 10, 0x10b981, 1);
      player.setStrokeStyle(2, 0xffffff, 1);

      cursors = this.input.keyboard.createCursorKeys();

      // make canvas click-through so DOM clicks still work
      const canvas = game.canvas;
      if (canvas) canvas.style.pointerEvents = 'none';
    }

    function clamp(v, min, max){ return Math.max(min, Math.min(max, v)); }

    function rectsIntersect(ax, ay, aw, ah, bx, by, bw, bh){
      return !(ax+aw < bx || ax > bx+bw || ay+ah < by || ay > by+bh);
    }

    function update(){
      if (!window.GameAPI) return;
      const state = window.GameAPI.state;
      let dx = 0, dy = 0;
      if (cursors.left?.isDown) dx -= 1;
      if (cursors.right?.isDown) dx += 1;
      if (cursors.up?.isDown) dy -= 1;
      if (cursors.down?.isDown) dy += 1;

      if (dx !== 0 || dy !== 0){
        const len = Math.hypot(dx, dy) || 1;
        const vx = (dx/len) * state.speed;
        const vy = (dy/len) * state.speed;
        const pw = 22, ph = 22;
        state.x = clamp(state.x + vx, 0, width - pw);
        state.y = clamp(state.y + vy, 0, height - ph);
        player.x = state.x + 11;
        player.y = state.y + 11;
        handleOverlap(state);
        positionPrompt(state);
      } else {
        // still check overlap changes when stationary if needed
        handleOverlap(state);
      }

      // E key to interact
      if (Phaser.Input.Keyboard.JustDown(this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E))){
        if (!state.popupOpen && lastOverlapKey){
          window.GameAPI.openLocationPopup(lastOverlapKey);
        }
      }
    }

    function handleOverlap(state){
      const pw = 22, ph = 22;
      let ov = null;
      for (const b of buildings){
        if (rectsIntersect(state.x, state.y, pw, ph, b.x, b.y, b.w, b.h)){
          ov = b; break;
        }
      }
      if (!ov){
        lastOverlapKey = null;
        if (state.suppressUntilExit) state.suppressUntilExit = false;
        hidePrompt();
        return;
      }
      if (state.suppressUntilExit){
        lastOverlapKey = ov.key;
        hidePrompt();
        return;
      }
      const changed = ov.key !== lastOverlapKey;
      lastOverlapKey = ov.key;
      if (!state.popupOpen){
        if (changed){
          window.GameAPI.openLocationPopup(ov.key);
        } else {
          showPromptNearPlayer();
        }
      }
    }

    function positionPrompt(state){
      const prompt = document.getElementById('interactPrompt');
      if (!prompt) return;
      const mapRect = mapEl.getBoundingClientRect();
      const cx = state.x + 11;
      const cy = state.y + 11;
      prompt.style.left = cx + 'px';
      prompt.style.top = cy + 'px';
      prompt.style.transform = 'translate(-50%, -120%)';
    }

    function showPromptNearPlayer(){
      const prompt = document.getElementById('interactPrompt');
      if (!prompt) return;
      prompt.classList.remove('hidden');
    }

    function hidePrompt(){
      const prompt = document.getElementById('interactPrompt');
      if (!prompt) return;
      prompt.classList.add('hidden');
    }
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', createPhaserScene);
  } else {
    createPhaserScene();
  }
})();
