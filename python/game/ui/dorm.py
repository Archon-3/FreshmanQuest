from ..popup import Popup


def build_popup(h):
    s = h['state']
    p = Popup("Dormitory")
    p.add_line("Welcome to campus. Rest and study here.")

    def sleep():
        h['setEnergy'](100)
        h['toast']("Energy restored to 100")

    def study():
        if not s.flags['dormStudyDone']:
            s.flags['dormStudyDone'] = True
            h['addXP'](10)
            h['toast']("+10 XP for studying")
            h['rebuild']()

    def take_key():
        if not s.flags['dormKey']:
            s.flags['dormKey'] = True
            h['addItem']('Dorm Key')
            h['toast']("Dorm Key collected")
            h['rebuild']()

    p.add_button("Sleep (Energy 100)", sleep, primary=True, disabled=False)
    p.add_button("Study (+10 XP)", study, disabled=s.flags['dormStudyDone'])
    p.add_button("Take Dorm Key", take_key, disabled=s.flags['dormKey'])
    return p
