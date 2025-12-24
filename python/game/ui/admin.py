from ..popup import Popup


def build_popup(h):
    s = h['state']
    p = Popup("Admin Office")
    p.add_line("Complete your registration tasks.")

    def get_id():
        if not s.flags['studentId']:
            if s.energy < 10:
                h['toast']("Too tired! Need at least 10 energy.")
                return
            s.flags['studentId'] = True
            h['addItem']('Student ID Card')
            h['addXP'](15)
            h['addReputation'](3)  # Official student status
            h['addEnergy'](-10)
            h['completeQuest']('studentId')
            h['toast']('Student ID collected (+15 XP, +3 Reputation)')
            h['rebuild']()

    def get_tt():
        if not s.flags['timetable']:
            s.flags['timetable'] = True
            h['addItem']('Timetable')
            h['completeQuest']('timetable')
            h['toast']('Timetable collected')
            h['rebuild']()

    p.add_button("Get Student ID (+15 XP)", get_id, primary=True, disabled=s.flags['studentId'])
    p.add_button("Collect Timetable", get_tt, primary=False, disabled=s.flags['timetable'])
    return p
