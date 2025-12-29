from ..popup import Popup

CATEGORIES = {
    'Engineering': ['Statics Basics', 'Digital Logic', 'Fluid Flow 101'],
    'Science': ['Physics Primer', 'Organic Chemistry', 'Biology of Cells'],
    'Literature': ['Poetry Classics', 'Modern Novels', 'World Myths']
}


def build_popup(h):
    s = h['state']
    p = Popup("Library")

    if not s.flags['libraryCard']:
        p.add_line("Register for a library card to access books.")
        def register():
            if s.energy < 10:
                h['toast']("Too tired! Need at least 10 energy.")
                return
            s.flags['libraryCard'] = True
            h['addItem']('Library Card')
            h['addXP'](20)
            h['addReputation'](5)  # Getting library card is a responsible action
            h['addEnergy'](-10)
            h['completeQuest']('libraryVisit')
            h['toast']("Library card registered (+20 XP, +5 Reputation)")
            h['rebuild']()
        p.add_button("Register (+20 XP)", register, primary=True)
        return p

    p.add_line("Browse and read books:")
    # Only one action at a time in this compact popup; rotate categories
    def make_read(title):
        def _read():
            if s.energy < 15:
                h['toast']("Too tired to read! Need at least 15 energy.")
                return
            s.meta['booksRead'] = int(s.meta.get('booksRead', 0)) + 1
            h['addXP'](2)
            knowledge_gain = 6
            # High knowledge makes reading more effective
            if s.knowledge > 50:
                knowledge_gain += 2
            h['addKnowledge'](knowledge_gain)
            h['addStress'](-2)  # Reading is relaxing
            h['addEnergy'](-15)
            h['addDiscipline'](2)
            h['toast'](f'Read: {title} (+2 XP, +{knowledge_gain} Knowledge, -2 Stress)')
            h['rebuild']()
        return _read

    added = 0
    for cat, books in CATEGORIES.items():
        for title in books:
            if added >= 3:
                break
            p.add_button(f"Read: {title}", make_read(title), primary=False)
            added += 1
        if added >= 3:
            break

    return p
