"""Player/Character class for D&D game"""
from .utils import roll_dice, calculate_modifier, load_json, save_json
from .classes import get_class_by_name, CharacterClass
from typing import Dict, List, Optional

class Player:
    """Represents the player character"""
    
    def __init__(self, name: str, character_class: str):
        self.name = name
        self.character_class = get_class_by_name(character_class)
        
        # Ability Scores (will be set during character creation)
        self.abilities = {
            "STR": 10,
            "DEX": 10,
            "CON": 10,
            "INT": 10,
            "WIS": 10,
            "CHA": 10
        }
        
        # Character progression
        self.level = 1
        self.experience = 0
        self.max_hp = 10
        self.current_hp = self.max_hp
        
        # Combat stats
        self.armor_class = 10
        self.proficiency_bonus = 2
        
        # Inventory
        self.inventory: List[Dict] = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_shield = None
        
        # Skills
        self.skills: Dict[str, int] = self._initialize_skills()
    
    def _initialize_skills(self) -> Dict[str, int]:
        """Initialize skill bonuses based on abilities"""
        return {
            "Acrobatics": calculate_modifier(self.abilities["DEX"]),
            "Animal Handling": calculate_modifier(self.abilities["WIS"]),
            "Arcana": calculate_modifier(self.abilities["INT"]),
            "Athletics": calculate_modifier(self.abilities["STR"]),
            "Deception": calculate_modifier(self.abilities["CHA"]),
            "History": calculate_modifier(self.abilities["INT"]),
            "Insight": calculate_modifier(self.abilities["WIS"]),
            "Intimidation": calculate_modifier(self.abilities["CHA"]),
            "Investigation": calculate_modifier(self.abilities["INT"]),
            "Medicine": calculate_modifier(self.abilities["WIS"]),
            "Perception": calculate_modifier(self.abilities["WIS"]),
            "Performance": calculate_modifier(self.abilities["CHA"]),
            "Persuasion": calculate_modifier(self.abilities["CHA"]),
            "Sleight of Hand": calculate_modifier(self.abilities["DEX"]),
            "Stealth": calculate_modifier(self.abilities["DEX"]),
            "Survival": calculate_modifier(self.abilities["WIS"]),
        }
    
    def set_abilities(self, abilities: Dict[str, int]):
        """Set ability scores and recalculate modifiers"""
        self.abilities = abilities
        self.skills = self._initialize_skills()
        self._update_hp()
        self._update_ac()
    
    def roll_ability_scores(self, method: str = "4d6") -> Dict[str, int]:
        """
        Roll ability scores using various methods.
        
        Args:
            method: "4d6" (drop lowest), "3d6", or "standard" (15,14,13,12,10,8)
        
        Returns:
            Dictionary of rolled ability scores
        """
        if method == "4d6":
            # Roll 4d6, drop lowest, do this 6 times
            rolls = []
            for _ in range(6):
                dice = [roll_dice(1, 6) for _ in range(4)]
                dice.sort()
                rolls.append(sum(dice[1:]))  # Drop lowest
            rolls.sort(reverse=True)
        elif method == "3d6":
            # Roll 3d6, do this 6 times
            rolls = [roll_dice(3, 6) for _ in range(6)]
            rolls.sort(reverse=True)
        elif method == "standard":
            # Standard array
            rolls = [15, 14, 13, 12, 10, 8]
        else:
            rolls = [10, 10, 10, 10, 10, 10]
        
        ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        return {ability: rolls[i] for i, ability in enumerate(ability_names)}
    
    def _update_hp(self):
        """Recalculate maximum HP"""
        con_mod = calculate_modifier(self.abilities["CON"])\n        self.max_hp = self.character_class.get_hit_points(con_mod, self.level)
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
    
    def _update_ac(self):
        """Recalculate armor class"""
        dex_mod = calculate_modifier(self.abilities["DEX"])
        self.armor_class = 10 + dex_mod
        
        # Apply armor bonus if equipped
        if self.equipped_armor:
            self.armor_class = self.equipped_armor.get("ac", 10)
            if self.equipped_armor.get("add_dex", False):
                self.armor_class += dex_mod
        
        # Apply shield bonus if equipped
        if self.equipped_shield:
            self.armor_class += self.equipped_shield.get("ac_bonus", 2)
    
    def add_item(self, item: Dict) -> bool:
        """Add item to inventory"""
        self.inventory.append(item)
        return True
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.inventory):
            if item.get("name").lower() == item_name.lower():
                self.inventory.pop(i)
                return True
        return False
    
    def equip_weapon(self, weapon_name: str) -> bool:
        """Equip a weapon from inventory"""
        for item in self.inventory:
            if item.get("type") == "weapon" and item.get("name").lower() == weapon_name.lower():
                self.equipped_weapon = item
                return True
        return False
    
    def equip_armor(self, armor_name: str) -> bool:
        """Equip armor from inventory"""
        for item in self.inventory:
            if item.get("type") == "armor" and item.get("name").lower() == armor_name.lower():
                self.equipped_armor = item
                self._update_ac()
                return True
        return False
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to player"""
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp
    
    def heal(self, amount: int) -> int:
        """Heal player"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp
    
    def level_up(self):
        """Increase level by 1"""
        self.level += 1
        self.proficiency_bonus = 2 + (self.level - 1) // 4
        self._update_hp()
        self.current_hp = self.max_hp
    
    def add_experience(self, xp: int):
        """Add experience and check for level up"""
        self.experience += xp
        # XP threshold: 300 * (level ^ 2)
        xp_threshold = 300 * (self.level ** 2)
        
        while self.experience >= xp_threshold:
            self.experience -= xp_threshold
            self.level_up()
            xp_threshold = 300 * (self.level ** 2)
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving"""
        return {
            "name": self.name,
            "class": self.character_class.name.lower(),
            "level": self.level,
            "experience": self.experience,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "abilities": self.abilities,
            "armor_class": self.armor_class,
            "proficiency_bonus": self.proficiency_bonus,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "skills": self.skills,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from dictionary"""
        player = cls(data["name"], data["class"])
        player.level = data["level"]
        player.experience = data["experience"]
        player.current_hp = data["current_hp"]
        player.max_hp = data["max_hp"]
        player.abilities = data["abilities"]
        player.armor_class = data["armor_class"]
        player.proficiency_bonus = data["proficiency_bonus"]
        player.inventory = data["inventory"]
        player.equipped_weapon = data["equipped_weapon"]
        player.equipped_armor = data["equipped_armor"]
        player.skills = data["skills"]
        return player
    
    def display_sheet(self):
        """Display character sheet"""
        print(f"\n{'='*60}")
        print(f\"CHARACTER SHEET: {self.name}\".center(60))
        print(f\"{'='*60}\\n\")
        
        print(f\"Class: {self.character_class.name:20} Level: {self.level}\")
        print(f\"Experience: {self.experience:20} Proficiency Bonus: +{self.proficiency_bonus}\\n\")
        
        print(\"ABILITY SCORES:\")
        print(\"-\" * 40)
        for ability, score in self.abilities.items():
            mod = calculate_modifier(score)
            print(f\"{ability}: {score:2d} ({mod:+3d})\")
        
        print(f\"\\nAC: {self.armor_class:20} HP: {self.current_hp}/{self.max_hp}\\n\")
        
        if self.equipped_weapon:
            print(f\"Equipped Weapon: {self.equipped_weapon.get('name')}\")
        if self.equipped_armor:
            print(f\"Equipped Armor: {self.equipped_armor.get('name')}\\n\")
