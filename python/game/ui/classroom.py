from ..popup import Popup

SCHOOLS = {
    'civil': {
        'name': 'School of Civil & Water Resources',
        'departments': {
            'civil': 'Civil Engineering',
            'water': 'Water Resources Engineering'
        },
        'programCore': ['Calculus I', 'Physics I', 'Intro to Engineering'],
        'deptCourses': {
            'civil': ['Intro to Structures', 'Soil Mechanics', 'Surveying'],
            'water': ['Fluid Mechanics', 'Hydrology', 'Irrigation Engineering']
        }
    },
    'ece': {
        'name': 'School of Electrical & Computer',
        'departments': {
            'electrical': 'Electrical Engineering',
            'computer': 'Computer Engineering'
        },
        'programCore': ['Calculus I', 'Programming Basics', 'Digital Systems I'],
        'deptCourses': {
            'electrical': ['Circuit Analysis', 'Electromagnetics', 'Power Systems'],
            'computer': ['Programming I', 'Data Structures', 'Computer Architecture']
        }
    },
    'mech': {
        'name': 'School of Mechanical & Materials',
        'departments': {
            'mechanical': 'Mechanical Engineering',
            'materials': 'Materials Science'
        },
        'programCore': ['Calculus I', 'Engineering Graphics', 'Materials Basics'],
        'deptCourses': {
            'mechanical': ['Statics', 'Dynamics', 'Thermodynamics'],
            'materials': ['Materials Science', 'Manufacturing Processes', 'Strength of Materials']
        }
    }
}


def build_popup(h):
    s = h['state']
    p = Popup("Classroom")

    # always offer First Class badge once orientation is done
    if not s.flags['firstClassBadge'] and s.quests['programOrientation']:
        p.add_line("Attend your first class to earn your badge.")
        def first_class():
            if not s.flags['firstClassBadge'] and s.quests['programOrientation']:
                s.flags['firstClassBadge'] = True
                h['addItem']('First Class Badge')
                h['addXP'](10)
                h['completeQuest']('firstClass')
                h['toast']("First Class completed (+10 XP)")
                h['rebuild']()
        p.add_button("Attend First Class (+10 XP)", first_class, primary=False, disabled=not s.quests['programOrientation'])

    # choose school
    if not s.meta['school']:
        p.add_line("Choose your school:")
        for sid, sc in SCHOOLS.items():
            def _choose(sid=sid, name=sc['name']):
                s.meta['school'] = sid
                s.quests['programOrientation'] = False
                s.quests['completeProgramCourses'] = False
                s.quests['chooseDepartment'] = False
                s.quests['completeDepartmentCourses'] = False
                s.meta['department'] = None
                s.meta['programCourses'] = {}
                s.meta['courses'] = {}
                s.meta['coursesDone'] = 0
                h['completeQuest']('chooseSchool')
                h['addItem']('School: ' + name)
                h['rebuild']()
            p.add_button(sc['name'], _choose, primary=True)
        return p

    # orientation
    if not s.quests['programOrientation']:
        p.add_line("Program Orientation is required to start.")
        def orient():
            h['completeQuest']('programOrientation')
            h['addXP'](10)
            h['toast']("Orientation complete (+10 XP)")
            h['rebuild']()
        p.add_button("Attend Orientation (+10 XP)", orient, primary=True)
        return p

    # program core
    if not s.quests['completeProgramCourses']:
        sch = SCHOOLS[s.meta['school']]
        plist = sch['programCore']
        next_idx = 0
        for i,_ in enumerate(plist):
            k = f"pcourse:{s.meta['school']}:{i}"
            if not s.meta['programCourses'].get(k):
                next_idx = i
                break
        done = sum(1 for i,_ in enumerate(plist) if s.meta['programCourses'].get(f"pcourse:{s.meta['school']}:{i}"))
        p.add_line(f"Program core progress: {done}/{len(plist)}")
        def do_next():
            k = f"pcourse:{s.meta['school']}:{next_idx}"
            if not s.meta['programCourses'].get(k):
                s.meta['programCourses'][k] = True
                h['addXP'](5)
                if done + 1 >= len(plist):
                    h['completeQuest']('completeProgramCourses')
                h['rebuild']()
        p.add_button("Complete next core course (+5 XP)", do_next, primary=True)
        return p

    # choose department
    if not s.quests['chooseDepartment']:
        sch = SCHOOLS[s.meta['school']]
        p.add_line("Choose your department:")
        for did, name in sch['departments'].items():
            def _choose_dep(did=did, name=name):
                s.meta['department'] = { 'id': did, 'name': name, 'school': s.meta['school'] }
                h['completeQuest']('chooseDepartment')
                h['addItem']('Department: ' + name)
                h['rebuild']()
            p.add_button(name, _choose_dep, primary=True)
        return p

    # department courses
    if not s.quests['completeDepartmentCourses']:
        sch = SCHOOLS[s.meta['school']]
        dep_id = s.meta['department']['id']
        dlist = sch['deptCourses'][dep_id]
        next_idx = 0
        for i,_ in enumerate(dlist):
            k = f"course:{s.meta['school']}:{dep_id}:{i}"
            if not s.meta['courses'].get(k):
                next_idx = i
                break
        done = sum(1 for i,_ in enumerate(dlist) if s.meta['courses'].get(f"course:{s.meta['school']}:{dep_id}:{i}"))
        p.add_line(f"Dept course progress: {done}/{len(dlist)}")
        def do_next_dep():
            k = f"course:{s.meta['school']}:{dep_id}:{next_idx}"
            if not s.meta['courses'].get(k):
                s.meta['courses'][k] = True
                h['addXP'](5)
                if done + 1 >= len(dlist):
                    h['completeQuest']('completeDepartmentCourses')
                h['rebuild']()
        p.add_button("Complete next dept course (+5 XP)", do_next_dep, primary=True)
        return p

    # completed path fallback
    p.add_line("You have completed the academic progression.")
    return p
