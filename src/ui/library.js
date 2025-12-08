(function(){
  window.UI = window.UI || {};
  window.UI.library = function(container, state, {addXP, addItem, completeQuest}){
    function render(){
      container.innerHTML = '';
      const root = document.createElement('div');
      root.className = 'ui-grid';

      const card = document.createElement('div');
      card.className = 'ui-card';
      const title = document.createElement('div'); title.className = 'ui-title'; title.textContent = 'Library Services';
      card.appendChild(title);

      if (!state.flags.libraryCard) {
        const row = document.createElement('div'); row.className = 'hstack';
        const btn = document.createElement('button'); btn.className = 'btn primary'; btn.textContent = 'Register for Library Card (+20 XP)';
        btn.addEventListener('click', function(){ if(state.flags.libraryCard) return; state.flags.libraryCard = true; addItem('Library Card'); addXP(20); completeQuest('libraryVisit'); render(); });
        row.appendChild(btn);
        card.appendChild(row);
        root.appendChild(card);
        container.appendChild(root);
        return;
      }

      const booksCard = document.createElement('div');
      booksCard.className = 'ui-card';
      const t2 = document.createElement('div'); t2.className = 'ui-title'; t2.textContent = 'Browse Books';
      booksCard.appendChild(t2);

      const categories = {
        Engineering: ['Statics Basics', 'Digital Logic', 'Fluid Flow 101'],
        Science: ['Physics Primer', 'Organic Chemistry', 'Biology of Cells'],
        Literature: ['Poetry Classics', 'Modern Novels', 'World Myths']
      };

      const catGrid = document.createElement('div'); catGrid.className = 'ui-grid';
      Object.entries(categories).forEach(([cat, list]) => {
        const c = document.createElement('div'); c.className = 'ui-card';
        const h = document.createElement('div'); h.className = 'ui-title'; h.textContent = cat; c.appendChild(h);
        list.forEach(title => {
          const row = document.createElement('div'); row.className = 'hstack';
          const lbl = document.createElement('div'); lbl.textContent = title; row.appendChild(lbl);
          const btn = document.createElement('button'); btn.className = 'btn'; btn.textContent = 'Read (+2 XP)';
          btn.addEventListener('click', function(){ state.meta.booksRead = (state.meta.booksRead||0)+1; addXP(2); });
          row.appendChild(btn);
          c.appendChild(row);
        });
        catGrid.appendChild(c);
      });
      booksCard.appendChild(catGrid);

      const stats = document.createElement('div'); stats.className = 'ui-card';
      const t3 = document.createElement('div'); t3.className = 'ui-title'; t3.textContent = 'Reading Stats';
      const s = document.createElement('div'); s.className = 'ui-subtle'; s.textContent = 'Books read: ' + (state.meta.booksRead||0);
      stats.appendChild(t3); stats.appendChild(s);

      root.appendChild(card);
      root.appendChild(booksCard);
      root.appendChild(stats);
      container.appendChild(root);
    }

    render();
  };
})();
