"""Battle system for D&D game"""
from .utils import roll_dice, calculate_modifier, print_separator
from .player import Player
from .enemy import Enemy
from typing import Tuple, List

class Battle:
    """Handles combat between player and enemy"""
    
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.round = 0
        self.battle_log: List[str] = []
    
    def determine_initiative(self) -> Tuple[bool, int, int]:
        """
        Determine who goes first in combat.
        
        Returns:
            Tuple of (player_goes_first, player_initiative, enemy_initiative)
        """
        dex_mod_player = calculate_modifier(self.player.abilities["DEX"])
        dex_mod_enemy = calculate_modifier(self.enemy.abilities["DEX"])
        
        player_init = roll_dice(1, 20) + dex_mod_player
        enemy_init = roll_dice(1, 20) + dex_mod_enemy
        
        return player_init >= enemy_init, player_init, enemy_init
    
    def player_attack(self) -> Tuple[bool, int, int]:
        """
        Execute a player attack.
        
        Returns:
            Tuple of (hit, attack_roll, damage)
        """
        str_mod = calculate_modifier(self.player.abilities["STR"])
        dex_mod = calculate_modifier(self.player.abilities["DEX"])
        
        # Use best modifier for attack
        attack_bonus = max(str_mod, dex_mod) + self.player.proficiency_bonus
        
        # Attack roll
        attack_roll = roll_dice(1, 20) + attack_bonus
        
        # Check if it hits
        hit = attack_roll >= self.enemy.armor_class
        
        # Calculate damage if hit
        damage = 0
        if hit:
            if self.player.equipped_weapon:
                damage_dice, damage_type = self.player.equipped_weapon.get("damage", "1d4").split("d")
                damage = roll_dice(int(damage_dice), int(damage_type)) + attack_bonus
            else:
                # Unarmed strike
                damage = roll_dice(1, 4) + attack_bonus
        
        return hit, attack_roll, damage
    
    def enemy_attack(self) -> Tuple[bool, int, int]:
        """
        Execute an enemy attack.
        
        Returns:
            Tuple of (hit, attack_roll, damage)
        """
        attack_roll, attack_bonus, damage, _ = self.enemy.attack()
        hit = attack_roll >= self.player.armor_class
        
        if not hit:
            damage = 0
        
        return hit, attack_roll, damage
    
    def execute_round(self, player_action: str = "attack") -> bool:
        """
        Execute one round of combat.
        
        Args:
            player_action: "attack", "defend", "flee"
        
        Returns:
            True if battle continues, False if battle ends
        """
        self.round += 1
        print(f"\n{'='*60}")
        print(f"ROUND {self.round}".center(60))
        print(f"{'='*60}\n")
        
        # Player turn
        if player_action == "attack":
            hit, attack_roll, damage = self.player_attack()
            
            if hit:
                print(f"✓ {self.player.name} HITS! (Roll: {attack_roll})")
                print(f"  Damage: {damage}")
                self.enemy.take_damage(damage)
                self.battle_log.append(f"Round {self.round}: {self.player.name} dealt {damage} damage")
            else:
                print(f"✗ {self.player.name} MISSES! (Roll: {attack_roll})")
                self.battle_log.append(f"Round {self.round}: {self.player.name} missed")
        
        elif player_action == "defend":
            print(f"🛡️  {self.player.name} takes a defensive stance!")
            self.battle_log.append(f"Round {self.round}: {self.player.name} defended")
        
        # Check if enemy is dead
        if not self.enemy.is_alive():
            print(f"\n{'='*60}")
            print(f"🎉 VICTORY! {self.enemy.name} has been defeated!".center(60))
            print(f"{'='*60}\n")
            return False
        
        print_separator()
        
        # Enemy turn
        hit, attack_roll, damage = self.enemy_attack()
        
        if hit:
            print(f"✓ {self.enemy.name} HITS! (Roll: {attack_roll})")
            print(f"  Damage: {damage}")
            self.player.take_damage(damage)
            self.battle_log.append(f"Round {self.round}: {self.enemy.name} dealt {damage} damage")
        else:
            print(f"✗ {self.enemy.name} MISSES! (Roll: {attack_roll})")
            self.battle_log.append(f"Round {self.round}: {self.enemy.name} missed")
        
        print_separator()
        
        # Display status
        print(f"\n{self.player.name:20} HP: {self.player.current_hp}/{self.player.max_hp}")
        print(f"{self.enemy.name:20} HP: {self.enemy.current_hp}/{self.enemy.max_hp}\n")
        
        # Check if player is dead
        if self.player.current_hp <= 0:
            print(f"\n{'='*60}")
            print(f"💀 DEFEAT! {self.player.name} has been defeated!".center(60))
            print(f"{'='*60}\n")
            return False
        
        return True
    
    def start_battle(self) -> bool:
        """
        Start the battle and return winner.
        
        Returns:
            True if player won, False if player lost
        """
        print(f"\n{'='*60}")
        print(f"⚔️  BATTLE START! ⚔️".center(60))
        print(f"{'='*60}\n")
        
        print(f"{self.player.name} (HP: {self.player.current_hp}/{self.player.max_hp}, AC: {self.player.armor_class})")
        print(f"vs")
        print(f"{self.enemy.name} (HP: {self.enemy.current_hp}/{self.enemy.max_hp}, AC: {self.enemy.armor_class})\n")
        
        # Determine initiative
        player_first, player_init, enemy_init = self.determine_initiative()
        print(f"Initiative: {self.player.name} ({player_init}) vs {self.enemy.name} ({enemy_init})")
        print(f"{('Player' if player_first else 'Enemy')} goes first!\n")
        
        input("Press Enter to start combat...")
        
        # Combat loop
        while True:
            print("\nWhat do you do?")
            print("1. Attack")
            print("2. Defend")
            print("3. Flee")
            
            choice = input("\nYour choice (1-3): ").strip()
            
            if choice == "1":
                action = "attack"
            elif choice == "2":
                action = "defend"
            elif choice == "3":
                print(f"\n{self.player.name} fled from battle!")
                return False
            else:
                print("Invalid choice!")
                continue
            
            if not self.execute_round(action):
                break
        
        return self.player.current_hp > 0
