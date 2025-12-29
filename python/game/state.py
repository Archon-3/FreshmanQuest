from .consts import MAP_H

class GameState:
    def __init__(self):
        # Start player on main road (center of map vertically)
        # MAP_H = 560, so main road is at y = 280
        # PLAYER_SIZE = 22 (defined in main.py), so center player at y = 280 - 11 = 269
        self.x = 100
        self.y = 269  # Center on main road
        self.speed = 3
        
        # Core stats (0-100 range)
        self.energy = 80
        self.knowledge = 20  # Academic performance
        self.stress = 30  # Affects performance
        self.reputation = 25  # Social influence
        self.discipline = 40  # Long-term success factor
        
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
        
        # Time system
        self.day = 1  # Current day
        self.time_of_day = 'Morning'  # Morning, Afternoon, Evening, Night
        self.time_tick = 0  # Internal counter for time progression
        self.last_time_update = 0  # Track when time last updated (in game ticks)
        
        self.popup_open = False
        self.suppress_until_exit = False
        self.victory_awarded = False
        self.show_city_view = False
        self.transition_alpha = 0
        self.city_car_positions = [100, 300, 500, 700, 900]  # Initial car positions
        self.city_player_x = 600  # Start player in center of city road (SCREEN_W/2 = 600)
        self.city_player_y = 525  # On the city road (SCREEN_H - 75 = 525)
        self.collected_points = 0  # Track collected points/coins

    def reset(self):
        # Reset collectibles when resetting game
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
    
    def add_energy(self, v):
        """Add energy (can be negative)."""
        self.energy = max(0, min(100, self.energy + int(v)))
    
    def set_knowledge(self, v):
        self.knowledge = max(0, min(100, int(v)))
    
    def add_knowledge(self, v):
        """Add knowledge (can be negative)."""
        self.knowledge = max(0, min(100, self.knowledge + int(v)))
    
    def set_stress(self, v):
        self.stress = max(0, min(100, int(v)))
    
    def add_stress(self, v):
        """Add stress (can be negative)."""
        self.stress = max(0, min(100, self.stress + int(v)))
    
    def set_reputation(self, v):
        self.reputation = max(0, min(100, int(v)))
    
    def add_reputation(self, v):
        """Add reputation (can be negative)."""
        self.reputation = max(0, min(100, self.reputation + int(v)))
    
    def set_discipline(self, v):
        self.discipline = max(0, min(100, int(v)))
    
    def add_discipline(self, v):
        """Add discipline (can be negative)."""
        self.discipline = max(0, min(100, self.discipline + int(v)))
    
    def update_time(self, ticks_passed=1):
        """Update time system. Returns True if time of day changed."""
        self.time_tick += ticks_passed
        self.last_time_update += ticks_passed
        
        # Time progression: every 600 ticks (10 seconds at 60 FPS) = advance time of day
        # This means each time period lasts 10 seconds, full day cycle = 40 seconds
        old_time = self.time_of_day
        time_sequence = ['Morning', 'Afternoon', 'Evening', 'Night']
        current_idx = time_sequence.index(self.time_of_day)
        
        # Calculate how many time periods have passed
        periods_passed = self.time_tick // 600
        
        if periods_passed > 0:
            # Calculate new time index
            new_idx = (current_idx + periods_passed) % 4
            self.time_of_day = time_sequence[new_idx]
            
            # Calculate days passed
            total_periods = current_idx + periods_passed
            days_passed = total_periods // 4
            if days_passed > 0:
                self.day += days_passed
            
            # Reset time_tick to prevent overflow (keep remainder)
            self.time_tick = self.time_tick % 600
        
        # Return True if time of day changed
        return old_time != self.time_of_day
    
    def get_time_display(self):
        """Get formatted time string for display."""
        return f"Day {self.day} - {self.time_of_day}"
    
    def is_time(self, *times):
        """Check if current time matches any of the given times."""
        return self.time_of_day in times
    
    def can_access_building(self, building_key):
        """Check if building is accessible at current time."""
        # Cafeteria closed at night
        if building_key == 'cafeteria' and self.time_of_day == 'Night':
            return False
        # Library closed at night
        if building_key == 'library' and self.time_of_day == 'Night':
            return False
        # Admin office closed in evening and night
        if building_key == 'admin' and self.time_of_day in ['Evening', 'Night']:
            return False
        # Classroom closed at night (but open other times)
        if building_key == 'classroom' and self.time_of_day == 'Night':
            return False
        return True
    
    def process_stat_decay(self):
        """Process natural stat decay/regeneration based on time and discipline."""
        # High discipline reduces negative effects
        discipline_factor = max(0.3, 1.0 - (self.discipline / 150.0))  # 0.3 to 1.0
        
        # Stress naturally increases slightly over time (unless high discipline)
        # More stress if already stressed (vicious cycle)
        stress_increase = 0.5 * discipline_factor
        if self.stress > 70:
            stress_increase *= 1.5  # High stress makes it worse
        self.add_stress(stress_increase)
        
        # Knowledge decays very slowly if not maintained (only if discipline is low)
        if self.discipline < 30:
            knowledge_decay = 0.2 * (1.0 - discipline_factor)
            self.add_knowledge(-knowledge_decay)
        
        # Reputation decays slowly if discipline is low
        if self.discipline < 40:
            reputation_decay = 0.1 * (1.0 - discipline_factor)
            self.add_reputation(-reputation_decay)

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
