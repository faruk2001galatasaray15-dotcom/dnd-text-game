"""Utility functions for the D&D game"""
import random
import json
import os
from typing import List, Dict, Any

def roll_dice(num_dice: int = 1, dice_size: int = 20) -> int:
    """
    Roll dice and return the sum.
    
    Args:
        num_dice: Number of dice to roll
        dice_size: Size of each die (e.g., 20 for d20)
    
    Returns:
        Sum of all dice rolls
    """
    return sum(random.randint(1, dice_size) for _ in range(num_dice))

def calculate_modifier(stat: int) -> int:
    """
    Calculate ability modifier from stat value.
    Formula: (Stat - 10) / 2, rounded down
    
    Args:
        stat: The ability score (usually 1-20)
    
    Returns:
        The modifier value
    """
    return (stat - 10) // 2

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file safely.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Dictionary from JSON file, or empty dict if file doesn't exist
    """
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_json(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Save data to JSON file.
    
    Args:
        filepath: Path to save JSON file
        data: Dictionary to save
    
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text.center(56)}")
    print("="*60 + "\n")

def print_separator():
    """Print a separator line"""
    print("-" * 60)

def format_stat_table(stats: Dict[str, int]) -> str:
    """
    Format ability scores as a table.
    
    Args:
        stats: Dictionary of ability names and scores
    
    Returns:
        Formatted string representation
    """
    output = ""
    for stat, value in stats.items():
        modifier = calculate_modifier(value)
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        output += f"{stat:3s}: {value:2d} ({mod_str:+3s})\n"
    return output
