from ..popup import Popup


def build_popup(h):
    s = h['state']
    p = Popup("Dormitory")
    p.add_line("Welcome to campus. Rest and study here.")

    def sleep():
        if s.energy < 100 or s.stress > 0:
            # Sleep restores energy and reduces stress
            h['setEnergy'](100)
            stress_reduction = min(20, s.stress)
            h['addStress'](-stress_reduction)
            h['toast'](f"Energy restored to 100, Stress -{stress_reduction}")
        else:
            h['toast']("You're already well-rested!")

    def study():
        if s.energy < 20:
            h['toast']("Too tired to study! Need at least 20 energy.")
            return
        
        if not s.flags['dormStudyDone']:
            s.flags['dormStudyDone'] = True
            # Study increases knowledge but costs energy and adds stress
            knowledge_gain = 8
            stress_gain = 3
            energy_cost = 15
            
            # High stress reduces knowledge gain efficiency
            if s.stress > 70:
                knowledge_gain = int(knowledge_gain * 0.7)
            
            h['addXP'](10)
            h['addKnowledge'](knowledge_gain)
            h['addStress'](stress_gain)
            h['addEnergy'](-energy_cost)
            h['addDiscipline'](2)  # Studying builds discipline
            h['toast'](f"+10 XP, +{knowledge_gain} Knowledge, +{stress_gain} Stress, -{energy_cost} Energy")
            h['rebuild']()
        else:
            # Can study again, but with reduced rewards
            if s.energy < 15:
                h['toast']("Too tired to study! Need at least 15 energy.")
                return
            knowledge_gain = 5
            stress_gain = 2
            energy_cost = 15
            if s.stress > 70:
                knowledge_gain = int(knowledge_gain * 0.7)
            h['addXP'](5)
            h['addKnowledge'](knowledge_gain)
            h['addStress'](stress_gain)
            h['addEnergy'](-energy_cost)
            h['addDiscipline'](1)
            h['toast'](f"+5 XP, +{knowledge_gain} Knowledge, +{stress_gain} Stress, -{energy_cost} Energy")

    def take_key():
        if not s.flags['dormKey']:
            s.flags['dormKey'] = True
            h['addItem']('Dorm Key')
            h['toast']("Dorm Key collected")
            h['rebuild']()

    # Check if it's night time for better sleep benefits
    is_night = s.time_of_day == 'Night'
    sleep_text = "Sleep (Energy 100, Reduce Stress)" + (" - Night Bonus!" if is_night else "")
    
    p.add_button(sleep_text, sleep, primary=True, disabled=False)
    study_text = "Study" if s.flags['dormStudyDone'] else "Study (+10 XP)"
    p.add_button(study_text, study, disabled=s.energy < 15)
    p.add_button("Take Dorm Key", take_key, disabled=s.flags['dormKey'])
    return p
