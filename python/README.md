Freshman Quest (Python/Pygame)

Run locally
1) Install Python 3.10+
2) Create venv (optional) and install deps:
   pip install -r python/requirements.txt
3) Launch game:
   python python/main.py

Controls
- Arrow keys: Move
- E: Interact when near a building
- Esc: Close popups
- Mouse: Click buttons in popups

Notes
- The map is procedurally rendered (grass, paths, buildings, trees).
- Building UIs are modular and mirror the web version (Dorm, Classroom, Library, Cafeteria, Admin).
- Quests/XP/Inventory/Rank/energy are persisted in-memory during a run.
