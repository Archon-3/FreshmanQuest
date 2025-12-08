class GameState:
    def __init__(self):
        self.x = 100
        self.y = 470
        self.speed = 3
        self.energy = 80
        self.xp = 0
        self.inventory = set()
        self.quests = {
            'firstClass': False,
            'studentId': False,
            'libraryVisit': False,
            'timetable': False,
            'eatMeal': False,
            'chooseSchool': False,
            'programOrientation': False,
            'completeProgramCourses': False,
            'chooseDepartment': False,
            'completeDepartmentCourses': False
        }
        self.flags = {
            'dormKey': False,
            'firstClassBadge': False,
            'libraryCard': False,
            'mealCoupon': False,
            'studentId': False,
            'timetable': False,
            'ateMeal': False,
            'dormStudyDone': False
        }
        self.meta = {
            'school': None,
            'department': None,
            'coursesDone': 0,
            'courses': {},
            'programCourses': {},
            'booksRead': 0
        }
        self.popup_open = False
        self.suppress_until_exit = False
        self.victory_awarded = False

    def reset(self):
        self.__init__()

    def add_xp(self, n):
        self.xp += int(n)

    def add_item(self, name):
        self.inventory.add(str(name))

    def complete_quest(self, q):
        if q in self.quests and not self.quests[q]:
            self.quests[q] = True

    def set_energy(self, v):
        self.energy = max(0, min(100, int(v)))

    def rank_for_xp(self):
        x = self.xp
        if x >= 100:
            return 'Master'
        if x >= 60:
            return 'Achiever'
        if x >= 30:
            return 'Explorer'
        return 'Rookie'

    def all_quests_done(self):
        return all(self.quests.values())
