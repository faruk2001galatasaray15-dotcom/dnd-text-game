"""D&D 5e Character Classes"""
from typing import Dict, List

class CharacterClass:
    """Base class for D&D character classes"""
    
    def __init__(
        self,
        name: str,
        hit_die: int,
        proficiencies: List[str],
        ability_name: str,
        ability_description: str,
    ):
        self.name = name
        self.hit_die = hit_die  # d6, d8, d10, d12
        self.proficiencies = proficiencies
        self.ability_name = ability_name
        self.ability_description = ability_description
    
    def get_hit_points(self, constitution_modifier: int, level: int) -> int:
        """Calculate hit points based on level and CON modifier"""
        base_hp = self.hit_die
        additional_hp = (self.hit_die // 2 + 1) * (level - 1)
        return base_hp + additional_hp + (constitution_modifier * level)

# Predefined classes
WARRIOR = CharacterClass(
    name="Warrior",
    hit_die=10,
    proficiencies=["Simple Weapons", "Martial Weapons", "Heavy Armor", "Shields"],
    ability_name="Ezici Darbe",
    ability_description="Saldırıya +2 ve hasara +4 ekler.",
)

ROGUE = CharacterClass(
    name="Rogue",
    hit_die=8,
    proficiencies=["Simple Weapons", "Hand Crossbows", "Longswords", "Rapiers", "Shortswords", "Light Armor"],
    ability_name="Sinsi Saldırı",
    ability_description="Avantajlı saldırı yapar ve +1d6 hasar verir.",
)

MAGE = CharacterClass(
    name="Mage",
    hit_die=6,
    proficiencies=["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows", "Light Armor"],
    ability_name="Ateş Topu",
    ability_description="INT ile büyü saldırısı yapar ve 2d6 ateş hasarı verir.",
)

CLERIC = CharacterClass(
    name="Cleric",
    hit_die=8,
    proficiencies=["Simple Weapons", "Heavy Armor", "Shields"],
    ability_name="İyileştirici Dua",
    ability_description="1d8 + WIS kadar can yeniler.",
)

RANGER = CharacterClass(
    name="Ranger",
    hit_die=10,
    proficiencies=["Simple Melee Weapons", "Martial Melee Weapons", "Longswords", "Light Armor", "Medium Armor"],
    ability_name="Çifte Atış",
    ability_description="Aynı turda iki saldırı yapar.",
)

# Class dictionary for easy lookup
CLASSES = {
    "warrior": WARRIOR,
    "rogue": ROGUE,
    "mage": MAGE,
    "cleric": CLERIC,
    "ranger": RANGER,
}

def get_class_by_name(name: str) -> CharacterClass:
    """Get a character class by name"""
    return CLASSES.get(name.lower())

def list_classes() -> List[tuple]:
    """Return a list of available classes"""
    return list(CLASSES.items())
