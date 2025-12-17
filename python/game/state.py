from .consts import MAP_H

class GameState:
    def __init__(self):
        # Start player on main road (center of map vertically)
        # MAP_H = 560, so main road is at y = 280
        # PLAYER_SIZE = 22 (defined in main.py), so center player at y = 280 - 11 = 269
        self.x = 100
        self.y = 269  # Center on main road
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
        self.show_city_view = False
        self.transition_alpha = 0
        self.city_car_positions = [100, 300, 500, 700, 900]  # Initial car positions
        self.city_player_x = 600  # Start player in center of city road (SCREEN_W/2 = 600)
        self.city_player_y = 525  # On the city road (SCREEN_H - 75 = 525)

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
