(function(){
  window.UI = window.UI || {};
  window.UI.admin = function(container, state, {addXP, addItem, completeQuest}){
    const root = document.createElement('div');
    root.className = 'ui-grid';

    const reg = document.createElement('div');
    reg.className = 'ui-card';
    const t1 = document.createElement('div'); t1.className = 'ui-title'; t1.textContent = 'Student Services';
    const row1 = document.createElement('div'); row1.className = 'hstack';
    const idBtn = document.createElement('button'); idBtn.className = 'btn primary';
    idBtn.textContent = state.flags.studentId ? 'Student ID Collected' : 'Get Student ID (+15 XP)';
    idBtn.disabled = !!state.flags.studentId;
    idBtn.addEventListener('click', function(){ if(state.flags.studentId) return; state.flags.studentId = true; addItem('Student ID Card'); addXP(15); completeQuest('studentId'); idBtn.textContent = 'Student ID Collected'; idBtn.disabled = true; });
    row1.appendChild(idBtn);
    reg.appendChild(t1); reg.appendChild(row1);

    const schedule = document.createElement('div');
    schedule.className = 'ui-card';
    const t2 = document.createElement('div'); t2.className = 'ui-title'; t2.textContent = 'Timetable';
    const row2 = document.createElement('div'); row2.className = 'hstack';
    const ttBtn = document.createElement('button'); ttBtn.className = 'btn';
    ttBtn.textContent = state.flags.timetable ? 'Timetable Collected' : 'Collect Timetable';
    ttBtn.disabled = !!state.flags.timetable;
    ttBtn.addEventListener('click', function(){ if(state.flags.timetable) return; state.flags.timetable = true; addItem('Timetable'); completeQuest('timetable'); ttBtn.textContent = 'Timetable Collected'; ttBtn.disabled = true; });
    row2.appendChild(ttBtn);
    schedule.appendChild(t2); schedule.appendChild(row2);

    root.appendChild(reg);
    root.appendChild(schedule);
    container.appendChild(root);
  };
})();
