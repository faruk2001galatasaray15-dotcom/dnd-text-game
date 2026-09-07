"""Items and inventory system for D&D game"""
from typing import Dict, List, Optional

class Item:
    """Represents a game item"""
    
    def __init__(self, name: str, item_type: str, description: str = "", 
                 rarity: str = "common", value: int = 0):
        self.name = name
        self.item_type = item_type  # "weapon", "armor", "consumable", "quest"
        self.description = description
        self.rarity = rarity  # "common", "uncommon", "rare", "very rare", "legendary"
        self.value = value  # in gold pieces
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary"""
        return {
            "name": self.name,
            "type": self.item_type,
            "description": self.description,
            "rarity": self.rarity,
            "value": self.value
        }

class Weapon(Item):
    """Represents a weapon"""
    
    def __init__(self, name: str, damage: str, damage_type: str, 
                 weight: float = 1, properties: List[str] = None, **kwargs):
        super().__init__(name, "weapon", **kwargs)
        self.damage = damage  # e.g., "1d8", "2d6"
        self.damage_type = damage_type  # "slashing", "piercing", "bludgeoning"
        self.weight = weight
        self.properties = properties or []
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "damage": self.damage,
            "damage_type": self.damage_type,
            "weight": self.weight,
            "properties": self.properties
        })
        return data

class Armor(Item):
    """Represents armor"""
    
    def __init__(self, name: str, armor_class: int, armor_type: str,
                 weight: float = 1, add_dex: bool = False, **kwargs):
        super().__init__(name, "armor", **kwargs)
        self.armor_class = armor_class
        self.armor_type = armor_type  # "light", "medium", "heavy"
        self.weight = weight
        self.add_dex = add_dex  # Whether DEX modifier adds to AC
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "ac": self.armor_class,
            "armor_type": self.armor_type,
            "weight": self.weight,
            "add_dex": self.add_dex
        })
        return data

class Consumable(Item):
    """Represents consumable items"""
    
    def __init__(self, name: str, effect: str, effect_value: int = 0, **kwargs):
        super().__init__(name, "consumable", **kwargs)
        self.effect = effect  # "heal", "poison", "buff"
        self.effect_value = effect_value
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "effect": self.effect,
            "effect_value": self.effect_value
        })
        return data

# Predefined weapons
WEAPONS = {
    "shortsword": Weapon(
        name="Short Sword",
        damage="1d6",
        damage_type="piercing",
        weight=2,
        properties=["finesse", "light"],
        value=10,
        description="A classic blade, quick and deadly"
    ),
    "longsword": Weapon(
        name="Long Sword",
        damage="1d8",
        damage_type="slashing",
        weight=3,
        properties=["versatile"],
        value=15,
        description="A well-balanced sword"
    ),
    "greataxe": Weapon(
        name="Great Axe",
        damage="1d12",
        damage_type="slashing",
        weight=7,
        properties=["heavy", "two-handed"],
        value=30,
        description="A massive axe for crushing blows"
    ),
    "dagger": Weapon(
        name="Dagger",
        damage="1d4",
        damage_type="piercing",
        weight=1,
        properties=["finesse", "light", "thrown"],
        value=2,
        description="A small but deadly blade"
    ),
    "bow": Weapon(
        name="Long Bow",
        damage="1d8",
        damage_type="piercing",
        weight=2,
        properties=["ammunition", "heavy", "two-handed"],
        value=50,
        description="A ranged weapon for distant targets"
    ),
    "mace": Weapon(
        name="Mace",
        damage="1d6",
        damage_type="bludgeoning",
        weight=4,
        properties=["versatile"],
        value=5,
        description="A heavy blunt weapon"
    ),
}

# Predefined armor
ARMOR_ITEMS = {
    "leather": Armor(
        name="Leather Armor",
        armor_class=11,
        armor_type="light",
        weight=10,
        add_dex=True,
        value=5,
        description="Flexible and reliable"
    ),
    "chainmail": Armor(
        name="Chain Mail",
        armor_class=16,
        armor_type="heavy",
        weight=55,
        add_dex=False,
        value=75,
        description="Heavy but effective protection"
    ),
    "scale": Armor(
        name="Scale Mail",
        armor_class=14,
        armor_type="medium",
        weight=45,
        add_dex=False,
        value=50,
        description="Overlapping scales for protection"
    ),
    "studded": Armor(
        name="Studded Leather Armor",
        armor_class=12,
        armor_type="light",
        weight=13,
        add_dex=True,
        value=45,
        description="Leather with protective studs"
    ),
}

# Predefined consumables
CONSUMABLES = {
    "potion_healing": Consumable(
        name="Healing Potion",
        effect="heal",
        effect_value=2,  # 2d4+2
        value=50,
        description="Restores 2d4+2 HP"
    ),
    "potion_strength": Consumable(
        name="Potion of Strength",
        effect="buff",
        effect_value=5,  # +5 to STR for 1 hour
        value=100,
        description="Increases STR by 5 for 1 hour"
    ),
    "antidote": Consumable(
        name="Antidote",
        effect="cure_poison",
        effect_value=0,
        value=30,
        description="Cures poison"
    ),
}

# Inventory management
class Inventory:
    """Manages player inventory"""
    
    def __init__(self, max_weight: float = 300):
        self.items: List[Dict] = []
        self.max_weight = max_weight
        self.current_weight = 0
    
    def add_item(self, item: Dict, quantity: int = 1) -> bool:
        """Add item to inventory"""
        item_weight = item.get("weight", 0) * quantity
        
        if self.current_weight + item_weight > self.max_weight:
            return False  # Too heavy
        
        # Check if item already exists
        for inv_item in self.items:
            if inv_item["name"] == item["name"]:
                inv_item["quantity"] = inv_item.get("quantity", 1) + quantity
                self.current_weight += item_weight
                return True
        
        # Add new item
        item["quantity"] = quantity
        self.items.append(item)
        self.current_weight += item_weight
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.items):
            if item["name"].lower() == item_name.lower():
                item_qty = item.get("quantity", 1)
                
                if quantity >= item_qty:
                    self.current_weight -= item.get("weight", 0) * item_qty
                    self.items.pop(i)
                else:
                    item["quantity"] -= quantity
                    self.current_weight -= item.get("weight", 0) * quantity
                
                return True
        
        return False
    
    def get_item(self, item_name: str) -> Optional[Dict]:
        """Get item from inventory"""
        for item in self.items:
            if item["name"].lower() == item_name.lower():
                return item
        return None
    
    def list_items(self) -> str:
        """Get formatted list of inventory items"""
        if not self.items:
            return "Your inventory is empty."
        
        output = f"Inventory ({self.current_weight:.1f}/{self.max_weight} weight):\n"
        for item in self.items:
            qty = item.get("quantity", 1)
            qty_str = f" (x{qty})" if qty > 1 else ""
            output += f"  • {item['name']}{qty_str}\n"
        
        return output
    
    def to_dict(self) -> Dict:
        """Convert inventory to dictionary"""
        return {
            "items": self.items,
            "current_weight": self.current_weight,
            "max_weight": self.max_weight
        }
