"""Main game class for D&D Text Game"""
import os
import json
from typing import Optional
from .player import Player
from .enemy import Enemy, create_random_enemy
from .battle import Battle
from .items import WEAPONS, ARMOR_ITEMS, CONSUMABLES
from .classes import list_classes
from .utils import (
    clear_screen, print_header, print_separator, 
    load_json, save_json, format_stat_table
)

class Game:
    """Main game controller"""
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.is_running = True
        self.save_dir = "saves"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def display_title(self):
        """Display game title"""
        clear_screen()
        print("""
        ╔═══════════════════════════════════════════════════════════╗
        ║                                                           ║
        ║              🐉 D&D TEXT GAME 🐉                         ║
        ║         Metin Tabanlı Rol Yapma Oyunu                   ║
        ║                                                           ║
        ║         D&D 5e Mekaniklerine Sahip                       ║
        ║         Tek Oyunculu Macera Oyunu                        ║
        ║                                                           ║
        ╚═══════════════════════════════════════════════════════════╝
        """)
    
    def main_menu(self):
        """Display main menu"""
        while True:
            print("\n" + "="*60)
            print("MAIN MENU".center(60))
            print("="*60 + "\n")
            
            print("1. Yeni Oyun")
            print("2. Oyun Yükle")
            print("3. Çıkış\n")
            
            choice = input("Seçiniz (1-3): ").strip()
            
            if choice == "1":
                self.create_character()
                self.game_loop()
            elif choice == "2":
                if self.load_game():
                    self.game_loop()
            elif choice == "3":
                print("\nOyundan çıkılıyor...")
                self.is_running = False
                break
            else:
                print("Geçersiz seçim!")
    
    def create_character(self):
        """Character creation process"""
        clear_screen()
        print_header("KARAKTER OLUŞTURMA")
        
        # Get name
        name = input("Karakterinizin adını girin: ").strip()
        if not name:
            name = "Adventurer"
        
        # Choose class
        print("\nSınıf Seçin:")
        classes = list_classes()
        for i, (key, char_class) in enumerate(classes, 1):
            print(f"{i}. {char_class.name} (Hit Die: d{char_class.hit_die})")
        
        while True:
            choice = input("\nSınıf seçiniz (1-5): ").strip()
            if choice in ["1", "2", "3", "4", "5"]:
                class_key = list(dict(classes).keys())[int(choice) - 1]
                break
            print("Geçersiz seçim!")
        
        # Create player
        self.player = Player(name, class_key)
        
        # Ability score generation
        print("\n" + "="*60)
        print("Statü Atama Yöntemi")
        print("="*60)
        print("\n1. Rastgele (4d6, en düşüğü attır)")
        print("2. Standart Dizi (15, 14, 13, 12, 10, 8)")
        print("3. Eşit (10, 10, 10, 10, 10, 10)")
        
        method_choice = input("\nSeçiniz (1-3): ").strip()
        
        if method_choice == "1":
            abilities = self.player.roll_ability_scores("4d6")
        elif method_choice == "2":
            abilities = self.player.roll_ability_scores("standard")
        else:
            abilities = self.player.roll_ability_scores("equal")
        
        # Display and allow customization
        print("\n" + "="*60)
        print("Statüleriniz:")
        print("="*60 + "\n")
        print(format_stat_table(abilities))
        
        customize = input("\nStatülerinizi özelleştirmek istiyor musunuz? (e/h): ").strip().lower()
        if customize == "e":
            self.customize_abilities(abilities)
        
        self.player.set_abilities(abilities)
        
        # Starting inventory
        print("\n" + "="*60)
        print("Başlangıç Ekipmanı")
        print("="*60 + "\n")
        
        # Give starting weapon based on class
        if class_key == "warrior":
            weapon = WEAPONS["longsword"].to_dict()
            armor = ARMOR_ITEMS["chainmail"].to_dict()
            self.player.inventory.append(weapon)
            self.player.inventory.append(armor)
            self.player.equip_weapon("Long Sword")
            self.player.equip_armor("Chain Mail")
            print("Longsword ve Chain Mail ile başlıyorsunuz.")
        elif class_key == "rogue":
            weapon = WEAPONS["shortsword"].to_dict()
            armor = ARMOR_ITEMS["leather"].to_dict()
            self.player.inventory.append(weapon)
            self.player.inventory.append(armor)
            self.player.equip_weapon("Short Sword")
            self.player.equip_armor("Leather Armor")
            print("Short Sword ve Leather Armor ile başlıyorsunuz.")
        elif class_key == "mage":
            weapon = WEAPONS["dagger"].to_dict()
            armor = ARMOR_ITEMS["leather"].to_dict()
            self.player.inventory.append(weapon)
            self.player.inventory.append(armor)
            self.player.equip_weapon("Dagger")
            self.player.equip_armor("Leather Armor")
            print("Dagger ve Leather Armor ile başlıyorsunuz.")
        
        # Add healing potion
        potion = CONSUMABLES["potion_healing"].to_dict()
        potion["quantity"] = 2
        self.player.inventory.append(potion)
        
        print("\n2x Healing Potion eklendi.")
        
        input("\nDevam etmek için Enter'e basın...")
    
    def customize_abilities(self, abilities: dict):
        """Allow player to customize ability scores"""
        ability_names = list(abilities.keys())
        
        while True:
            print("\nHangi statüyü değiştirmek istiyorsunuz?")
            for i, ability in enumerate(ability_names, 1):
                print(f"{i}. {ability}: {abilities[ability]}")
            print("0. Tamam")
            
            choice = input("\nSeçiniz (0-6): ").strip()
            
            if choice == "0":
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(ability_names):
                    ability = ability_names[idx]
                    new_value = input(f"Yeni değer ({ability}): ").strip()
                    try:
                        abilities[ability] = int(new_value)
                    except ValueError:
                        print("Geçerli bir sayı girin!")
            except (ValueError, IndexError):
                print("Geçersiz seçim!")
    
    def game_loop(self):
        """Main game loop"""
        while self.is_running and self.player:
            clear_screen()
            print_header(f"{self.player.name} - Level {self.player.level} {self.player.character_class.name}")
            
            print(f"HP: {self.player.current_hp}/{self.player.max_hp}")
            print(f"AC: {self.player.armor_class}")
            print(f"XP: {self.player.experience}\n")
            
            print("="*60)
            print("NE YAPMAK İSTİYORSUNUZ?")
            print("="*60 + "\n")
            
            print("1. Düşman ile Savaş")
            print("2. Karakteri Görüntüle")
            print("3. Envanter")
            print("4. Beceriler")
            print("5. Oyunu Kaydet")
            print("6. Ana Menüye Dön\n")
            
            choice = input("Seçiniz (1-6): ").strip()
            
            if choice == "1":
                self.start_battle()
            elif choice == "2":
                self.view_character_sheet()
            elif choice == "3":
                self.view_inventory()
            elif choice == "4":
                self.view_skills()
            elif choice == "5":
                self.save_game()
            elif choice == "6":
                break
            else:
                print("Geçersiz seçim!")
                input("Devam etmek için Enter'e basın...")
    
    def start_battle(self):
        """Start a battle with a random enemy"""
        enemy = create_random_enemy(self.player.level)
        battle = Battle(self.player, enemy)
        
        player_won = battle.start_battle()
        
        if player_won:
            self.player.add_experience(enemy.experience_reward)
            print(f"\n{enemy.experience_reward} XP kazandınız!")
            
            # Drop loot
            if enemy.level > 1:
                loot = WEAPONS.get("shortsword", {})
                if loot:
                    self.player.inventory.append(loot)
                    print(f"\n{loot.get('name')} düştü!")
        else:
            print("\nOyun bitti...")
            self.is_running = False
        
        input("\nDevam etmek için Enter'e basın...")
    
    def view_character_sheet(self):
        """Display character sheet"""
        clear_screen()
        self.player.display_sheet()
        
        print("BECERİLER:")
        print("-" * 40)
        for skill, bonus in sorted(self.player.skills.items()):
            print(f"{skill:20} {bonus:+3d}")
        
        input("\nDevam etmek için Enter'e basın...")
    
    def view_inventory(self):
        """Display inventory"""
        clear_screen()
        print_header("ENVANTER")
        
        print(self.player.inventory)
        
        print("\n" + "="*60)
        print("SEÇENEKLER")
        print("="*60 + "\n")
        print("1. Silah Donat")
        print("2. Zırh Donat")
        print("3. Eşya Kullan")
        print("0. Geri Dön\n")
        
        choice = input("Seçiniz: ").strip()
        
        if choice == "1":
            item_name = input("Donatacak silahın adı: ").strip()
            if self.player.equip_weapon(item_name):
                print(f"✓ {item_name} donatıldı!")
            else:
                print("✗ Silah bulunamadı!")
        elif choice == "2":
            item_name = input("Donatacak zırhın adı: ").strip()
            if self.player.equip_armor(item_name):
                print(f"✓ {item_name} donatıldı!")
            else:
                print("✗ Zırh bulunamadı!")
        
        input("\nDevam etmek için Enter'e basın...")
    
    def view_skills(self):
        """Display skills"""
        clear_screen()
        print_header("BECERİLER")
        
        print(f"\nSınıf: {self.player.character_class.name}")
        print(f"Uzmanlaşma Bonusu: +{self.player.proficiency_bonus}\n")
        
        print("="*60)
        print("BECERİ LİSTESİ")
        print("="*60 + "\n")
        
        for skill, bonus in sorted(self.player.skills.items()):
            print(f"{skill:20} {bonus:+3d}")
        
        input("\nDevam etmek için Enter'e basın...")
    
    def save_game(self):
        """Save game to file"""
        filename = input("Kaydı adlandırın (varsayılan: save): ").strip()
        if not filename:
            filename = "save"
        
        filepath = os.path.join(self.save_dir, f"{filename}.json")
        
        save_data = self.player.to_dict()
        
        if save_json(filepath, save_data):
            print(f"\n✓ Oyun '{filename}' olarak kaydedildi!")
        else:
            print("\n✗ Kayıt başarısız oldu!")
        
        input("Devam etmek için Enter'e basın...")
    
    def load_game(self) -> bool:
        """Load game from file"""
        clear_screen()
        print_header("OYUN YÜKLE")
        
        # List available saves
        saves = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
        
        if not saves:
            print("Kaydedilmiş oyun bulunamadı!")
            input("Devam etmek için Enter'e basın...")
            return False
        
        print("Kaydedilmiş Oyunlar:\n")
        for i, save in enumerate(saves, 1):
            print(f"{i}. {save[:-5]}")
        
        choice = input("\nYüklenecek oyunu seçiniz (0 iptal): ").strip()
        
        try:
            idx = int(choice) - 1
            if idx < 0:
                return False
            
            if 0 <= idx < len(saves):
                filepath = os.path.join(self.save_dir, saves[idx])
                save_data = load_json(filepath)
                
                self.player = Player.from_dict(save_data)
                print(f"\n✓ '{saves[idx][:-5]}' yüklendi!")
                input("Devam etmek için Enter'e basın...")
                return True
        except ValueError:
            pass
        
        print("\n✗ Yükleme başarısız oldu!")
        input("Devam etmek için Enter'e basın...")
        return False
    
    def run(self):
        """Start the game"""
        self.display_title()
        self.main_menu()
