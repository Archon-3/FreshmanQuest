(function(){
  window.UI = window.UI || {};
  window.UI.dorm = function(container, state, {addXP, addItem, setEnergy}){
    const root = document.createElement('div');
    root.className = 'ui-grid';

    const room = document.createElement('div');
    room.className = 'ui-card';
    const t1 = document.createElement('div'); t1.className = 'ui-title'; t1.textContent = 'Your Room';
    const s1 = document.createElement('div'); s1.className = 'ui-subtle'; s1.textContent = 'Rest and study here.';
    const actions1 = document.createElement('div'); actions1.className = 'hstack';
    const sleepBtn = document.createElement('button'); sleepBtn.className = 'btn primary'; sleepBtn.textContent = 'Sleep (Energy 100)';
    sleepBtn.addEventListener('click', function(){ setEnergy(100); });
    const studyBtn = document.createElement('button'); studyBtn.className = 'btn'; studyBtn.textContent = state.flags.dormStudyDone ? 'Study Done' : 'Study at Desk (+10 XP)';
    studyBtn.disabled = !!state.flags.dormStudyDone;
    studyBtn.addEventListener('click', function(){ if(!state.flags.dormStudyDone){ state.flags.dormStudyDone = true; addXP(10); studyBtn.textContent = 'Study Done'; studyBtn.disabled = true; }});
    actions1.appendChild(sleepBtn); actions1.appendChild(studyBtn);
    room.appendChild(t1); room.appendChild(s1); room.appendChild(actions1);

    const items = document.createElement('div');
    items.className = 'ui-card';
    const t2 = document.createElement('div'); t2.className = 'ui-title'; t2.textContent = 'Essentials';
    const actions2 = document.createElement('div'); actions2.className = 'hstack';
    const keyBtn = document.createElement('button'); keyBtn.className = 'btn'; keyBtn.textContent = state.flags.dormKey ? 'Dorm Key Collected' : 'Take Dorm Key';
    keyBtn.disabled = !!state.flags.dormKey;
    keyBtn.addEventListener('click', function(){ if(!state.flags.dormKey){ state.flags.dormKey = true; addItem('Dorm Key'); keyBtn.textContent = 'Dorm Key Collected'; keyBtn.disabled = true; }});
    actions2.appendChild(keyBtn);
    items.appendChild(t2); items.appendChild(actions2);

    const decor = document.createElement('div');
    decor.className = 'ui-card';
    const t3 = document.createElement('div'); t3.className = 'ui-title'; t3.textContent = 'Furniture';
    const s3 = document.createElement('div'); s3.className = 'ui-subtle'; s3.textContent = 'Bed, study table, lamp.';
    decor.appendChild(t3); decor.appendChild(s3);

    root.appendChild(room);
    root.appendChild(items);
    root.appendChild(decor);

    container.appendChild(root);
  };
})();
