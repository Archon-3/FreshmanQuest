(function(){
  window.UI = window.UI || {};
  window.UI.classroom = function(container, state, {addXP, addItem, completeQuest}){
    function render(){
      container.innerHTML = '';
      const root = document.createElement('div');
      root.className = 'ui-grid';

      const schools = {
        civil: {
          name: 'School of Civil & Water Resources',
          departments: {
            civil: 'Civil Engineering',
            water: 'Water Resources Engineering'
          },
          courses: {
            civil: ['Intro to Structures', 'Soil Mechanics', 'Surveying'],
            water: ['Fluid Mechanics', 'Hydrology', 'Irrigation Engineering']
          },
          programCore: ['Calculus I', 'Physics I', 'Intro to Engineering']
        },
        ece: {
          name: 'School of Electrical & Computer',
          departments: {
            electrical: 'Electrical Engineering',
            computer: 'Computer Engineering'
          },
          courses: {
            electrical: ['Circuit Analysis', 'Electromagnetics', 'Power Systems'],
            computer: ['Programming I', 'Data Structures', 'Computer Architecture']
          },
          programCore: ['Calculus I', 'Programming Basics', 'Digital Systems I']
        },
        mech: {
          name: 'School of Mechanical & Materials',
          departments: {
            mechanical: 'Mechanical Engineering',
            materials: 'Materials Science'
          },
          courses: {
            mechanical: ['Statics', 'Dynamics', 'Thermodynamics'],
            materials: ['Materials Science', 'Manufacturing Processes', 'Strength of Materials']
          },
          programCore: ['Calculus I', 'Engineering Graphics', 'Materials Basics']
        }
      };

      function card(title){
        const c = document.createElement('div');
        c.className = 'ui-card';
        const h = document.createElement('div'); h.className = 'ui-title'; h.textContent = title; c.appendChild(h);
        return {c, h};
      }

      const schoolCard = card('Choose School');
      const schoolGrid = document.createElement('div'); schoolGrid.className = 'ui-grid';
      Object.entries(schools).forEach(([sid, s]) => {
        const sc = document.createElement('div'); sc.className = 'ui-card';
        const t = document.createElement('div'); t.className = 'ui-title'; t.textContent = s.name; sc.appendChild(t);
        const act = document.createElement('div'); act.className = 'hstack';
        const btn = document.createElement('button'); btn.className = 'btn primary';
        btn.textContent = state.meta.school === sid ? 'Selected' : 'Select';
        btn.disabled = state.meta.school === sid;
        btn.addEventListener('click', function(){
          state.meta.school = sid;
          // Reset downstream progression when switching school
          state.quests.programOrientation = false;
          state.quests.completeProgramCourses = false;
          state.quests.chooseDepartment = false;
          state.quests.completeDepartmentCourses = false;
          state.meta.department = null;
          state.meta.courses = {};
          state.meta.coursesDone = 0;
          state.meta.programCourses = {};
          completeQuest('chooseSchool');
          addItem('School: ' + s.name);
          render();
        });
        act.appendChild(btn);
        if (state.meta.school === sid) {
          const pill = document.createElement('div'); pill.className = 'pill'; pill.textContent = 'Current'; act.appendChild(pill);
        }
        sc.appendChild(act);
        schoolGrid.appendChild(sc);
      });
      schoolCard.c.appendChild(schoolGrid);
      root.appendChild(schoolCard.c);

      const orientationCard = card('Program Orientation');
      const oRow = document.createElement('div'); oRow.className = 'hstack';
      const oBtn = document.createElement('button'); oBtn.className = 'btn primary';
      const oriented = state.quests.programOrientation;
      oBtn.textContent = oriented ? 'Orientation Completed' : 'Attend Orientation (+10 XP)';
      oBtn.disabled = oriented || !state.meta.school;
      oBtn.addEventListener('click', function(){ if(!state.meta.school || oriented) return; completeQuest('programOrientation'); addXP(10); render(); });
      oRow.appendChild(oBtn);
      orientationCard.c.appendChild(oRow);
      root.appendChild(orientationCard.c);

      const firstClassCard = card('First Class');
      const fRow = document.createElement('div'); fRow.className = 'hstack';
      const fBtn = document.createElement('button'); fBtn.className = 'btn';
      const firstClassDone = state.flags.firstClassBadge;
      fBtn.textContent = firstClassDone ? 'First Class Completed' : 'Attend First Class (+10 XP)';
      fBtn.disabled = firstClassDone || !state.quests.programOrientation;
      fBtn.addEventListener('click', function(){ if(firstClassDone || !state.quests.programOrientation) return; state.flags.firstClassBadge = true; addItem('First Class Badge'); addXP(10); completeQuest('firstClass'); render(); });
      fRow.appendChild(fBtn);
      firstClassCard.c.appendChild(fRow);
      root.appendChild(firstClassCard.c);

      // Program Core Courses (must finish before choosing department)
      if (state.meta.school && state.quests.programOrientation) {
        const schId = state.meta.school;
        const plist = (schools[schId] && schools[schId].programCore) || [];
        const pCard = card('Program Core Courses');
        const pProg = document.createElement('div'); pProg.className = 'progress';
        const pFill = document.createElement('div'); pFill.className = 'fill';
        pProg.appendChild(pFill); pCard.c.appendChild(pProg);
        const pGrid = document.createElement('div'); pGrid.className = 'ui-grid';
        let pDone = 0;
        let nextPIdx = plist.findIndex((_, i) => !state.meta.programCourses['pcourse:' + schId + ':' + i]);
        if (nextPIdx === -1) nextPIdx = plist.length;
        plist.forEach((title, idx) => {
          const pc = document.createElement('div'); pc.className = 'ui-card';
          const t = document.createElement('div'); t.className = 'ui-title'; t.textContent = title; pc.appendChild(t);
          const k = 'pcourse:' + schId + ':' + idx;
          const done = !!state.meta.programCourses[k];
          if (done) pDone += 1;
          const act = document.createElement('div'); act.className = 'hstack';
          const btn = document.createElement('button');
          const canDo = !done && idx === nextPIdx;
          btn.className = done ? 'btn' : (canDo ? 'btn primary' : 'btn');
          btn.textContent = done ? 'Completed' : (canDo ? 'Complete (+5 XP)' : 'Locked');
          btn.disabled = done || !canDo;
          btn.addEventListener('click', function(){ if (state.meta.programCourses[k] || !canDo) return; state.meta.programCourses[k] = true; addXP(5); if (pDone + 1 >= plist.length) { completeQuest('completeProgramCourses'); } render(); });
          act.appendChild(btn); pc.appendChild(act); pGrid.appendChild(pc);
        });
        const pPct = plist.length ? Math.round((pDone / plist.length) * 100) : 0;
        pFill.style.width = pPct + '%';
        const pLabel = document.createElement('div'); pLabel.className = 'ui-subtle'; pLabel.textContent = 'Progress: ' + pDone + ' / ' + plist.length;
        pCard.c.appendChild(pLabel);
        pCard.c.appendChild(pGrid);
        root.appendChild(pCard.c);
      }

      const deptCard = card('Choose Department');
      const canChooseDept = !!state.meta.school && state.quests.programOrientation && state.quests.completeProgramCourses;
      const deptGrid = document.createElement('div'); deptGrid.className = 'ui-grid';
      if (state.meta.school) {
        const ds = schools[state.meta.school].departments;
        Object.entries(ds).forEach(([did, name]) => {
          const dc = document.createElement('div'); dc.className = 'ui-card';
          const t = document.createElement('div'); t.className = 'ui-title'; t.textContent = name; dc.appendChild(t);
          const actions = document.createElement('div'); actions.className = 'hstack';
          const btn = document.createElement('button'); btn.className = 'btn primary';
          const isCurrent = state.meta.department && state.meta.department.id === did && state.meta.department.school === state.meta.school;
          btn.textContent = isCurrent ? 'Selected' : 'Select';
          btn.disabled = !canChooseDept || isCurrent;
          btn.addEventListener('click', function(){ if(!canChooseDept || isCurrent) return; state.meta.department = { id: did, name, school: state.meta.school }; completeQuest('chooseDepartment'); addItem('Department: ' + name); render(); });
          actions.appendChild(btn);
          if (isCurrent) { const pill = document.createElement('div'); pill.className = 'pill'; pill.textContent = 'Current'; actions.appendChild(pill); }
          dc.appendChild(actions);
          deptGrid.appendChild(dc);
        });
      }
      deptCard.c.appendChild(deptGrid);
      root.appendChild(deptCard.c);

      if (state.meta.department) {
        const depId = state.meta.department.id;
        const schId = state.meta.department.school;
        const list = schools[schId].courses[depId] || [];
        const coursesCard = card('Department Courses');
        // Progress bar
        const progWrap = document.createElement('div'); progWrap.className = 'progress';
        const fill = document.createElement('div'); fill.className = 'fill';
        progWrap.appendChild(fill);
        coursesCard.c.appendChild(progWrap);
        const cGrid = document.createElement('div'); cGrid.className = 'ui-grid';
        let doneCount = 0;
        // Determine next unlock index
        let nextIdx = list.findIndex((_, i) => !state.meta.courses['course:' + schId + ':' + depId + ':' + i]);
        if (nextIdx === -1) nextIdx = list.length; // all done
        list.forEach((title, idx) => {
          const cc = document.createElement('div'); cc.className = 'ui-card';
          const t = document.createElement('div'); t.className = 'ui-title'; t.textContent = title; cc.appendChild(t);
          const k = 'course:' + schId + ':' + depId + ':' + idx;
          const done = !!state.meta.courses[k];
          if (done) doneCount += 1;
          const act = document.createElement('div'); act.className = 'hstack';
          const btn = document.createElement('button');
          const canDo = !done && idx === nextIdx; // sequential unlocking
          btn.className = done ? 'btn' : (canDo ? 'btn primary' : 'btn');
          btn.textContent = done ? 'Completed' : (canDo ? 'Complete (+5 XP)' : 'Locked');
          btn.disabled = done || !canDo;
          btn.addEventListener('click', function(){ if (state.meta.courses[k] || !canDo) return; state.meta.courses[k] = true; addXP(5); render(); });
          act.appendChild(btn);
          cc.appendChild(act);
          cGrid.appendChild(cc);
        });
        state.meta.coursesDone = doneCount;
        if (list.length > 0 && doneCount >= list.length) completeQuest('completeDepartmentCourses');
        const pct = list.length ? Math.round((doneCount / list.length) * 100) : 0;
        fill.style.width = pct + '%';
        const progLabel = document.createElement('div'); progLabel.className = 'ui-subtle'; progLabel.textContent = 'Progress: ' + doneCount + ' / ' + list.length;
        coursesCard.c.appendChild(progLabel);
        coursesCard.c.appendChild(cGrid);
        root.appendChild(coursesCard.c);
      }

      container.appendChild(root);
    }

    render();
  };
})();
