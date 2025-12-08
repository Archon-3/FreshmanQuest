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
            s.flags['libraryCard'] = True
            h['addItem']('Library Card')
            h['addXP'](20)
            h['completeQuest']('libraryVisit')
            h['toast']("Library card registered (+20 XP)")
            h['rebuild']()
        p.add_button("Register (+20 XP)", register, primary=True)
        return p

    p.add_line("Browse and read books:")
    # Only one action at a time in this compact popup; rotate categories
    def make_read(title):
        def _read():
            s.meta['booksRead'] = int(s.meta.get('booksRead', 0)) + 1
            h['addXP'](2)
            h['toast'](f'Read: {title} (+2 XP)')
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
