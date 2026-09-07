"""Enemy/Monster class for D&D game"""
import random
from .utils import roll_dice, calculate_modifier
from typing import Dict

class Enemy:
    """Represents an enemy/monster in the game"""
    
    def __init__(self, name: str, level: int = 1, enemy_type: str = "goblin"):
        self.name = name
        self.level = level
        self.enemy_type = enemy_type
        
        # Ability scores
        self.abilities = {
            "STR": random.randint(8, 16),
            "DEX": random.randint(8, 16),
            "CON": random.randint(8, 16),
            "INT": random.randint(3, 12),
            "WIS": random.randint(8, 14),
            "CHA": random.randint(3, 12)
        }
        
        # Combat stats
        self.armor_class = 10 + calculate_modifier(self.abilities["DEX"])
        self.max_hp = self._calculate_hp()
        self.current_hp = self.max_hp
        
        # Weapons and drops
        self.weapon = self._get_weapon()
        self.experience_reward = 100 * level
    
    def _calculate_hp(self) -> int:
        """Calculate hit points"""
        con_mod = calculate_modifier(self.abilities["CON"])
        base_hp = 4 + (self.level * 3)
        return max(1, base_hp + (con_mod * self.level))
    
    def _get_weapon(self) -> Dict:
        """Get a weapon for this enemy"""
        weapons = {
            "goblin": {"name": "Short Sword", "damage": "1d6", "damage_type": "piercing"},
            "orc": {"name": "Great Axe", "damage": "1d12", "damage_type": "slashing"},
            "skeleton": {"name": "Rusty Sword", "damage": "1d8", "damage_type": "slashing"},
            "zombie": {"name": "Bare Hands", "damage": "1d4", "damage_type": "bludgeoning"},
            "troll": {"name": "Large Club", "damage": "2d6", "damage_type": "bludgeoning"},
            "kobold": {"name": "Kobold Spear", "damage": "1d6", "damage_type": "piercing"},
            "bandit": {"name": "Scimitar", "damage": "1d6", "damage_type": "slashing"},
            "giant_spider": {"name": "Poisonous Bite", "damage": "1d8", "damage_type": "poison"},
            "ogre": {"name": "Heavy Club", "damage": "2d8", "damage_type": "bludgeoning"},
            "wraith": {"name": "Necrotic Touch", "damage": "2d6", "damage_type": "necrotic"},
            "dragon": {"name": "Dragon Breath", "damage": "6d6", "damage_type": "fire"},
        }
        return weapons.get(self.enemy_type, {"name": "Dagger", "damage": "1d4", "damage_type": "piercing"})
    
    def attack(self) -> tuple:
        """
        Calculate an attack roll and potential damage.
        
        Returns:
            Tuple of (attack_roll, hit_bonus, damage_roll, weapon_name)
        """
        str_mod = calculate_modifier(self.abilities["STR"])
        dex_mod = calculate_modifier(self.abilities["DEX"])
        
        # Use DEX for finesse weapons, STR for others
        attack_bonus = max(str_mod, dex_mod) + 2
        
        # Attack roll (d20 + modifier)
        attack_roll = roll_dice(1, 20) + attack_bonus
        
        # Damage roll
        damage_dice, damage_type = self.weapon["damage"].split("d")
        damage_roll = roll_dice(int(damage_dice), int(damage_type)) + attack_bonus
        
        return attack_roll, attack_bonus, damage_roll, self.weapon["name"]
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to enemy"""
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp
    
    def is_alive(self) -> bool:
        """Check if enemy is still alive"""
        return self.current_hp > 0
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary"""
        return {
            "name": self.name,
            "level": self.level,
            "type": self.enemy_type,
            "abilities": self.abilities,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "armor_class": self.armor_class,
            "weapon": self.weapon,
            "experience_reward": self.experience_reward
        }

# Enemy templates
ENEMY_TEMPLATES = {
    "goblin": {
        "name": "Goblin",
        "hp_base": 4,
        "ac_base": 12,
        "weapon": {"name": "Short Sword", "damage": "1d6", "damage_type": "piercing"},
        "xp": 50
    },
    "orc": {
        "name": "Orc",
        "hp_base": 8,
        "ac_base": 13,
        "weapon": {"name": "Great Axe", "damage": "1d12", "damage_type": "slashing"},
        "xp": 100
    },
    "skeleton": {
        "name": "Skeleton",
        "hp_base": 5,
        "ac_base": 13,
        "weapon": {"name": "Rusty Sword", "damage": "1d8", "damage_type": "slashing"},
        "xp": 75
    },
    "zombie": {
        "name": "Zombie",
        "hp_base": 6,
        "ac_base": 8,
        "weapon": {"name": "Bare Hands", "damage": "1d4", "damage_type": "bludgeoning"},
        "xp": 60
    },
    "troll": {
        "name": "Troll",
        "hp_base": 12,
        "ac_base": 15,
        "weapon": {"name": "Large Club", "damage": "2d6", "damage_type": "bludgeoning"},
        "xp": 200
    },
    "kobold": {
        "name": "Kobold",
        "hp_base": 3,
        "ac_base": 12,
        "weapon": {"name": "Kobold Spear", "damage": "1d6", "damage_type": "piercing"},
        "xp": 40
    },
    "bandit": {
        "name": "Bandit",
        "hp_base": 6,
        "ac_base": 12,
        "weapon": {"name": "Scimitar", "damage": "1d6", "damage_type": "slashing"},
        "xp": 80
    },
    "giant_spider": {
        "name": "Dev Örümcek",
        "hp_base": 10,
        "ac_base": 14,
        "weapon": {"name": "Poisonous Bite", "damage": "1d8", "damage_type": "poison"},
        "xp": 150
    },
    "ogre": {
        "name": "Ogre",
        "hp_base": 18,
        "ac_base": 11,
        "weapon": {"name": "Heavy Club", "damage": "2d8", "damage_type": "bludgeoning"},
        "xp": 250
    },
    "wraith": {
        "name": "Wraith",
        "hp_base": 14,
        "ac_base": 13,
        "weapon": {"name": "Necrotic Touch", "damage": "2d6", "damage_type": "necrotic"},
        "xp": 300
    }
}

def create_random_enemy(level: int = 1) -> Enemy:
    """Create a random enemy for the current level"""
    enemy_types = list(ENEMY_TEMPLATES.keys())
    enemy_type = random.choice(enemy_types)
    enemy = Enemy(f"Level {level} {ENEMY_TEMPLATES[enemy_type]['name']}", level, enemy_type)
    return enemy

def create_enemy(enemy_type: str, level: int = 1) -> Enemy:
    """Create a specific enemy selected by the player"""
    if enemy_type not in ENEMY_TEMPLATES:
        raise ValueError(f"Unknown enemy type: {enemy_type}")

    template = ENEMY_TEMPLATES[enemy_type]
    return Enemy(f"Level {level} {template['name']}", level, enemy_type)
