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
        self.ability_cooldown = 0
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
    
    def player_attack(
        self,
        attack_bonus_bonus: int = 0,
        damage_bonus: int = 0,
        advantage: bool = False,
    ) -> Tuple[bool, int, int]:
        """
        Execute a player attack.
        
        Returns:
            Tuple of (hit, attack_roll, damage)
        """
        str_mod = calculate_modifier(self.player.abilities["STR"])
        dex_mod = calculate_modifier(self.player.abilities["DEX"])
        
        # Use best modifier for attack
        attack_bonus = (
            max(str_mod, dex_mod)
            + self.player.proficiency_bonus
            + attack_bonus_bonus
        )
        
        # Attack roll
        rolls = [roll_dice(1, 20), roll_dice(1, 20)] if advantage else [roll_dice(1, 20)]
        attack_roll = max(rolls) + attack_bonus
        
        # Check if it hits
        hit = attack_roll >= self.enemy.armor_class
        
        # Calculate damage if hit
        damage = 0
        if hit:
            if self.player.equipped_weapon:
                damage_dice, damage_type = self.player.equipped_weapon.get("damage", "1d4").split("d")
                damage = roll_dice(int(damage_dice), int(damage_type)) + attack_bonus + damage_bonus
            else:
                # Unarmed strike
                damage = roll_dice(1, 4) + attack_bonus + damage_bonus
        
        return hit, attack_roll, max(0, damage)

    def use_class_ability(self):
        """Use the character's class-specific combat ability"""
        class_name = self.player.character_class.name.lower()
        ability_name = self.player.character_class.ability_name
        self.ability_cooldown = 3
        print(f"\n✨ {self.player.name} uses {ability_name}!")

        if class_name == "warrior":
            hit, attack_roll, damage = self.player_attack(
                attack_bonus_bonus=2,
                damage_bonus=4,
            )
            if hit:
                print(f"✓ Ezici darbe isabet etti! (Roll: {attack_roll})")
                print(f"  Damage: {damage}")
                self.enemy.take_damage(damage)
            else:
                print(f"✗ Ezici darbe ıska geçti! (Roll: {attack_roll})")

        elif class_name == "rogue":
            sneak_damage = roll_dice(1, 6)
            hit, attack_roll, damage = self.player_attack(
                damage_bonus=sneak_damage,
                advantage=True,
            )
            if hit:
                print(f"✓ Sinsi saldırı isabet etti! (Roll: {attack_roll})")
                print(f"  Damage: {damage} (sinsi saldırı bonusu: +{sneak_damage})")
                self.enemy.take_damage(damage)
            else:
                print(f"✗ Sinsi saldırı ıska geçti! (Roll: {attack_roll})")

        elif class_name == "mage":
            int_mod = calculate_modifier(self.player.abilities["INT"])
            attack_bonus = int_mod + self.player.proficiency_bonus
            attack_roll = roll_dice(1, 20) + attack_bonus
            if attack_roll >= self.enemy.armor_class:
                damage = max(1, roll_dice(2, 6) + int_mod)
                print(f"✓ Ateş topu isabet etti! (Roll: {attack_roll})")
                print(f"  Fire damage: {damage}")
                self.enemy.take_damage(damage)
            else:
                print(f"✗ Ateş topu ıska geçti! (Roll: {attack_roll})")

        elif class_name == "cleric":
            wis_mod = calculate_modifier(self.player.abilities["WIS"])
            heal_amount = max(1, roll_dice(1, 8) + wis_mod)
            old_hp = self.player.current_hp
            self.player.heal(heal_amount)
            actual_heal = self.player.current_hp - old_hp
            print(f"✓ İyileştirici Dua {actual_heal} HP yeniledi.")

        elif class_name == "ranger":
            total_damage = 0
            hits = 0
            for _ in range(2):
                if not self.enemy.is_alive():
                    break
                hit, attack_roll, damage = self.player_attack()
                if hit:
                    hits += 1
                    total_damage += damage
                    self.enemy.take_damage(damage)
                    print(f"✓ Çifte atış isabet etti! (Roll: {attack_roll}, Damage: {damage})")
                else:
                    print(f"✗ Çifte atış ıska geçti! (Roll: {attack_roll})")
            if hits:
                print(f"Toplam hasar: {total_damage}")
    
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
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
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

        elif player_action == "ability":
            self.use_class_ability()
        
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
            if self.ability_cooldown == 0:
                print(f"3. {self.player.character_class.ability_name}")
            else:
                print(
                    f"3. {self.player.character_class.ability_name} "
                    f"(cooldown: {self.ability_cooldown} tur)"
                )
            print("4. Flee")
            
            choice = input("\nYour choice (1-4): ").strip()
            
            if choice == "1":
                action = "attack"
            elif choice == "2":
                action = "defend"
            elif choice == "3":
                if self.ability_cooldown > 0:
                    print("Bu yetenek henüz hazır değil.")
                    continue
                action = "ability"
            elif choice == "4":
                print(f"\n{self.player.name} fled from battle!")
                return False
            else:
                print("Invalid choice!")
                continue
            
            if not self.execute_round(action):
                break
        
        return self.player.current_hp > 0
