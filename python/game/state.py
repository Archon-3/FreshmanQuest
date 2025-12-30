import random
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
        
        # Achievement system
        self.achievements = {
            'firstSteps': False,  # Complete first quest
            'coinCollector': False,  # Collect 10 coins
            'coinMaster': False,  # Collect 50 coins
            'cityExplorer': False,  # Visit city for first time
            'nightOwl': False,  # Complete activity at night
            'earlyBird': False,  # Complete activity in morning
            'socialButterfly': False,  # Reach 50 reputation
            'scholar': False,  # Reach 50 knowledge
            'zenMaster': False,  # Keep stress below 20 for 3 days
            'speedDemon': False,  # Collect 5 coins in one day
            'perfectDay': False,  # Complete all quests in one day
            'veteran': False  # Reach day 10
        }
        
        # Daily challenges
        self.daily_challenges = {
            'collect_coins': {'target': 5, 'current': 0, 'reward': 10},
            'visit_buildings': {'target': 3, 'current': 0, 'reward': 15},
            'maintain_stress': {'target': 50, 'current': 0, 'reward': 20},  # Keep stress below target
            'gain_knowledge': {'target': 10, 'current': 0, 'reward': 25}
        }
        self.last_challenge_reset_day = 1
        
        # Skill/Upgrade system (purchased with coins)
        self.upgrades = {
            'speed': 0,  # Max level 5, +1 speed per level
            'energy_max': 0,  # Max level 3, +10 energy per level
            'coin_magnet': 0,  # Max level 3, increases coin collection radius
            'stress_resistance': 0,  # Max level 3, reduces stress gain
            'knowledge_boost': 0  # Max level 3, increases knowledge gain
        }
        
        # Random events
        self.active_events = []  # List of active random events
        self.event_cooldown = 0  # Cooldown before next event
        
        # Streak system
        self.daily_streak = 0  # Consecutive days with activity
        self.last_active_day = 0
        
        # Difficulty scaling
        self.difficulty_level = 1  # Increases with progress
        self.stress_multiplier = 1.0  # Increases with difficulty

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
        # Apply knowledge boost upgrade
        knowledge_boost = self.upgrades.get('knowledge_boost', 0) * 0.2  # 20% boost per level
        v = v * (1.0 + knowledge_boost)
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
        # Apply stress resistance upgrade
        stress_resistance = self.upgrades.get('stress_resistance', 0) * 0.15  # 15% reduction per level
        stress_increase = 0.5 * discipline_factor * (1.0 - stress_resistance)
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
    
    def check_achievements(self):
        """Check and unlock achievements based on current state."""
        # First steps
        if not self.achievements['firstSteps'] and any(self.quests.values()):
            self.achievements['firstSteps'] = True
            return "Achievement Unlocked: First Steps!"
        
        # Coin achievements
        if not self.achievements['coinCollector'] and self.collected_points >= 10:
            self.achievements['coinCollector'] = True
            return "Achievement Unlocked: Coin Collector!"
        if not self.achievements['coinMaster'] and self.collected_points >= 50:
            self.achievements['coinMaster'] = True
            return "Achievement Unlocked: Coin Master!"
        
        # City explorer
        if not self.achievements['cityExplorer'] and self.show_city_view:
            self.achievements['cityExplorer'] = True
            return "Achievement Unlocked: City Explorer!"
        
        # Reputation
        if not self.achievements['socialButterfly'] and self.reputation >= 50:
            self.achievements['socialButterfly'] = True
            return "Achievement Unlocked: Social Butterfly!"
        
        # Knowledge
        if not self.achievements['scholar'] and self.knowledge >= 50:
            self.achievements['scholar'] = True
            return "Achievement Unlocked: Scholar!"
        
        # Veteran
        if not self.achievements['veteran'] and self.day >= 10:
            self.achievements['veteran'] = True
            return "Achievement Unlocked: Veteran!"
        
        return None
    
    def update_daily_challenges(self):
        """Reset daily challenges if new day."""
        if self.day > self.last_challenge_reset_day:
            self.last_challenge_reset_day = self.day
            # Reset challenge progress
            self.daily_challenges['collect_coins']['current'] = 0
            self.daily_challenges['visit_buildings']['current'] = 0
            self.daily_challenges['maintain_stress']['current'] = 0
            self.daily_challenges['gain_knowledge']['current'] = 0
    
    def check_daily_challenges(self):
        """Check if daily challenges are completed and award rewards."""
        rewards = []
        for challenge_key, challenge in self.daily_challenges.items():
            if challenge_key == 'maintain_stress':
                # For stress, check if current stress is below target
                if self.stress <= challenge['target']:
                    challenge['current'] = 1
                else:
                    challenge['current'] = 0
            elif challenge_key == 'gain_knowledge':
                # For knowledge, track how much gained today
                if challenge['current'] >= challenge['target']:
                    rewards.append(f"Daily Challenge Complete: {challenge_key} (+{challenge['reward']} XP)")
                    self.add_xp(challenge['reward'])
                    challenge['current'] = 0  # Reset after completion
            else:
                if challenge['current'] >= challenge['target']:
                    rewards.append(f"Daily Challenge Complete: {challenge_key} (+{challenge['reward']} XP)")
                    self.add_xp(challenge['reward'])
                    challenge['current'] = 0  # Reset after completion
        return rewards
    
    def purchase_upgrade(self, upgrade_key):
        """Purchase an upgrade using coins."""
        upgrade_costs = {
            'speed': [5, 10, 15, 20, 25],  # 5 levels
            'energy_max': [10, 20, 30],  # 3 levels
            'coin_magnet': [8, 15, 25],  # 3 levels
            'stress_resistance': [12, 25, 40],  # 3 levels
            'knowledge_boost': [10, 20, 30]  # 3 levels
        }
        
        if upgrade_key not in self.upgrades:
            return False, "Invalid upgrade"
        
        current_level = self.upgrades[upgrade_key]
        costs = upgrade_costs.get(upgrade_key, [])
        
        if current_level >= len(costs):
            return False, "Upgrade maxed out"
        
        cost = costs[current_level]
        if self.collected_points < cost:
            return False, f"Not enough coins! Need {cost}, have {self.collected_points}"
        
        self.collected_points -= cost
        self.upgrades[upgrade_key] += 1
        
        # Apply upgrade effects
        if upgrade_key == 'speed':
            self.speed = 3 + self.upgrades['speed']  # Base speed 3
        elif upgrade_key == 'energy_max':
            # Energy max is handled in add_energy
            pass
        
        return True, f"Upgrade purchased! {upgrade_key} level {self.upgrades[upgrade_key]}"
    
    def update_streak(self):
        """Update daily streak if player was active today."""
        if self.day > self.last_active_day:
            if self.last_active_day == self.day - 1:
                # Consecutive day
                self.daily_streak += 1
            else:
                # Streak broken
                self.daily_streak = 1
            self.last_active_day = self.day
    
    def get_streak_bonus(self):
        """Get XP bonus based on streak."""
        if self.daily_streak >= 7:
            return 0.5  # 50% bonus
        elif self.daily_streak >= 3:
            return 0.25  # 25% bonus
        return 0
    
    def update_difficulty(self):
        """Update difficulty based on player progress."""
        # Difficulty increases with day and XP
        base_difficulty = min(5, (self.day - 1) // 2 + 1)
        xp_difficulty = min(3, self.xp // 30)
        self.difficulty_level = base_difficulty + xp_difficulty
        
        # Stress multiplier increases with difficulty
        self.stress_multiplier = 1.0 + (self.difficulty_level - 1) * 0.2
    
    def trigger_random_event(self):
        """Trigger a random event based on game state."""
        if self.event_cooldown > 0:
            self.event_cooldown -= 1
            return None
        
        # Events trigger randomly (5% chance per frame when conditions met)
        if random.random() < 0.05:
            event_types = []
            
            # Stress event (if stress is high)
            if self.stress > 60:
                event_types.append('stress_relief')
            
            # Knowledge event (if knowledge is low)
            if self.knowledge < 40:
                event_types.append('study_opportunity')
            
            # Coin event (always available)
            event_types.append('coin_bonus')
            
            # Energy event (if energy is low)
            if self.energy < 50:
                event_types.append('energy_boost')
            
            if event_types:
                event_type = random.choice(event_types)
                self.event_cooldown = 300  # 5 seconds cooldown at 60 FPS
                
                if event_type == 'stress_relief':
                    self.add_stress(-10)
                    return "Random Event: Found a quiet spot! Stress -10"
                elif event_type == 'study_opportunity':
                    self.add_knowledge(5)
                    return "Random Event: Study group session! Knowledge +5"
                elif event_type == 'coin_bonus':
                    bonus = random.randint(2, 5)
                    self.collected_points += bonus
                    return f"Random Event: Found {bonus} coins on the ground!"
                elif event_type == 'energy_boost':
                    self.add_energy(15)
                    return "Random Event: Energy drink found! Energy +15"
        
        return None
