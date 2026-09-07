"""Main game class for D&D Text Game"""
import os
import json
import random
from typing import Optional
from .player import Player
from .enemy import Enemy, create_enemy, ENEMY_TEMPLATES
from .battle import Battle
from .items import WEAPONS, ARMOR_ITEMS, CONSUMABLES
from .classes import list_classes
from .utils import (
    clear_screen, print_header, print_separator, 
    load_json, save_json, format_stat_table, roll_dice
)

QUESTS = {
    "goblin_hunt": {
        "name": "Goblin Avı",
        "description": "İki goblini yenerek köy yolunu temizle.",
        "targets": ["goblin"],
        "target_count": 2,
        "reward_xp": 150,
        "reward_gold": 75,
    },
    "undead_threat": {
        "name": "Ölülerin Tehdidi",
        "description": "İki iskelet veya zombiyi yen.",
        "targets": ["skeleton", "zombie"],
        "target_count": 2,
        "reward_xp": 225,
        "reward_gold": 100,
    },
    "troll_bounty": {
        "name": "Troll Ödülü",
        "description": "Tehlikeli bir trollü alt et.",
        "targets": ["troll"],
        "target_count": 1,
        "reward_xp": 350,
        "reward_gold": 175,
    },
}

RANDOM_ENCOUNTERS = [
    {
        "name": "Yol Kesen Devriye",
        "description": "Düşmanlar yolunuzu kesti!",
        "kind": "battle",
        "enemies": ["goblin", "kobold", "bandit"],
    },
    {
        "name": "Zehirli Orman",
        "description": "Çalılıkların arasından dev bir örümcek çıktı!",
        "kind": "battle",
        "enemies": ["giant_spider"],
    },
    {
        "name": "Terk Edilmiş Sandık",
        "description": "Yol kenarında eski bir sandık buldunuz.",
        "kind": "treasure",
    },
    {
        "name": "Şifalı Pınar",
        "description": "Ormanda berrak bir pınar keşfettiniz.",
        "kind": "healing",
    },
    {
        "name": "Gizli Tuzak",
        "description": "Yerdeki ipi fark edemediniz; bir tuzak tetiklendi!",
        "kind": "trap",
    },
]

class Game:
    """Main game controller"""
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.is_running = True
        self.save_dir = "saves"
        self.active_quests = {}
        self.completed_quests = []
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
                self.is_running = True
                self.active_quests = {}
                self.completed_quests = []
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
        elif class_key == "cleric":
            weapon = WEAPONS["mace"].to_dict()
            armor = ARMOR_ITEMS["scale"].to_dict()
            self.player.inventory.append(weapon)
            self.player.inventory.append(armor)
            self.player.equip_weapon("Mace")
            self.player.equip_armor("Scale Mail")
            print("Mace ve Scale Mail ile başlıyorsunuz.")
        elif class_key == "ranger":
            weapon = WEAPONS["bow"].to_dict()
            armor = ARMOR_ITEMS["studded"].to_dict()
            self.player.inventory.append(weapon)
            self.player.inventory.append(armor)
            self.player.equip_weapon("Long Bow")
            self.player.equip_armor("Studded Leather Armor")
            print("Long Bow ve Studded Leather Armor ile başlıyorsunuz.")
        
        # Add healing potion
        potion = CONSUMABLES["potion_healing"].to_dict()
        potion["quantity"] = 2
        self.player.inventory.append(potion)
        
        print("\n2x Healing Potion eklendi.")
        
        input("\nDevam etmek için Enter'e basın...")
        self.is_running = True
    
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
            print(f"XP: {self.player.experience}")
            print(f"Altın: {self.player.gold}\n")
            
            print("="*60)
            print("NE YAPMAK İSTİYORSUNUZ?")
            print("="*60 + "\n")
            
            print("1. Düşman Seçerek Savaş")
            print("2. Rastgele Karşılaşma")
            print("3. Karakteri Görüntüle")
            print("4. Envanter")
            print("5. Beceriler")
            print("6. Görevler")
            print("7. Mağaza")
            print("8. Oyunu Kaydet")
            print("9. Ana Menüye Dön\n")
            
            choice = input("Seçiniz (1-9): ").strip()
            
            if choice == "1":
                self.start_battle()
            elif choice == "2":
                self.random_encounter()
            elif choice == "3":
                self.view_character_sheet()
            elif choice == "4":
                self.view_inventory()
            elif choice == "5":
                self.view_skills()
            elif choice == "6":
                self.quest_screen()
            elif choice == "7":
                self.store()
            elif choice == "8":
                self.save_game()
            elif choice == "9":
                break
            else:
                print("Geçersiz seçim!")
                input("Devam etmek için Enter'e basın...")
    
    def start_battle(self):
        """Let the player choose an enemy and start a battle"""
        enemy = self.choose_enemy()
        if enemy is None:
            return
        self.run_battle(enemy)

    def run_battle(self, enemy: Enemy):
        """Run a battle and process its rewards"""
        battle = Battle(self.player, enemy)
        
        player_won = battle.start_battle()
        
        if player_won:
            self.player.add_experience(enemy.experience_reward)
            print(f"\n{enemy.experience_reward} XP kazandınız!")
            gold_reward = max(10, enemy.level * 10)
            self.player.gold += gold_reward
            print(f"{gold_reward} altın kazandınız!")
            self.update_quest_progress(enemy)
            
            # Drop loot
            if enemy.level > 1:
                loot = WEAPONS.get("shortsword")
                if loot:
                    loot_data = loot.to_dict()
                    self.player.inventory.append(loot_data)
                    print(f"\n{loot.name} düştü!")
        elif self.player.current_hp <= 0:
            print("\nOyun bitti...")
            self.is_running = False
        else:
            print("\nSavaştan kaçtınız.")
        
        input("\nDevam etmek için Enter'e basın...")

    def random_encounter(self):
        """Resolve a random non-combat or combat encounter"""
        encounter = random.choice(RANDOM_ENCOUNTERS)
        clear_screen()
        print_header(f"RASTGELE KARŞILAŞMA: {encounter['name']}")
        print(f"{encounter['description']}\n")

        if encounter["kind"] == "battle":
            enemy_type = random.choice(encounter["enemies"])
            enemy = create_enemy(enemy_type, max(1, self.player.level))
            print(f"Karşınızda: {enemy.name}")
            input("Savaşa hazırlanmak için Enter'e basın...")
            self.run_battle(enemy)
            return

        if encounter["kind"] == "treasure":
            gold = roll_dice(2, 20) + 10
            self.player.gold += gold
            print(f"Sandıktan {gold} altın çıktı!")
        elif encounter["kind"] == "healing":
            healing = roll_dice(2, 4) + 2
            old_hp = self.player.current_hp
            self.player.heal(healing)
            print(f"Pınar {self.player.current_hp - old_hp} HP yeniledi.")
        elif encounter["kind"] == "trap":
            damage = max(1, roll_dice(1, 6) + self.player.level)
            self.player.take_damage(damage)
            print(f"Tuzak {damage} hasar verdi!")
            if self.player.current_hp <= 0:
                print("Yaralarınız ölümcül oldu...")
                self.is_running = False

        input("\nDevam etmek için Enter'e basın...")

    def choose_enemy(self) -> Optional[Enemy]:
        """Display available enemies and return the selected enemy"""
        clear_screen()
        print_header("DÜŞMAN SEÇİMİ")
        print(f"Seviyeniz: {self.player.level}\n")

        enemy_types = list(ENEMY_TEMPLATES.keys())
        recommended_levels = {
            "goblin": 1,
            "skeleton": 1,
            "zombie": 1,
            "kobold": 1,
            "bandit": 1,
            "orc": 2,
            "giant_spider": 2,
            "troll": 3,
            "ogre": 4,
            "wraith": 5,
        }

        for index, enemy_type in enumerate(enemy_types, 1):
            template = ENEMY_TEMPLATES[enemy_type]
            recommended = recommended_levels.get(enemy_type, 1)
            print(
                f"{index}. {template['name']:10} | "
                f"Önerilen seviye: {recommended} | "
                f"Ödül: yaklaşık {template['xp']} XP"
            )
        print("0. Geri dön\n")

        choice = input("Karşılaşma seçiniz: ").strip()
        if choice == "0":
            return None

        try:
            enemy_type = enemy_types[int(choice) - 1]
        except (ValueError, IndexError):
            print("Geçersiz seçim!")
            input("Devam etmek için Enter'e basın...")
            return None

        recommended = recommended_levels.get(enemy_type, 1)
        enemy_level = max(self.player.level, recommended)
        return create_enemy(enemy_type, enemy_level)

    def quest_screen(self):
        """View, accept, and track quests"""
        clear_screen()
        print_header("GÖREVLER")

        print("AKTİF GÖREVLER")
        print("-" * 60)
        if self.active_quests:
            for quest_id, progress in self.active_quests.items():
                quest = QUESTS[quest_id]
                print(
                    f"• {quest['name']}: {progress}/{quest['target_count']} "
                    f"- {quest['description']}"
                )
        else:
            print("Aktif göreviniz yok.")

        print("\nTAMAMLANAN GÖREVLER")
        print("-" * 60)
        completed_names = [
            QUESTS[quest_id]["name"] for quest_id in self.completed_quests
        ]
        print(", ".join(completed_names) if completed_names else "Henüz görev tamamlanmadı.")

        available = [
            (quest_id, quest)
            for quest_id, quest in QUESTS.items()
            if quest_id not in self.active_quests and quest_id not in self.completed_quests
        ]
        if not available:
            input("\nTüm görevleri aldınız veya tamamladınız. Geri dönmek için Enter...")
            return

        print("\nALINABİLECEK GÖREVLER")
        print("-" * 60)
        for index, (_, quest) in enumerate(available, 1):
            print(
                f"{index}. {quest['name']} - {quest['description']} "
                f"(Ödül: {quest['reward_xp']} XP, {quest['reward_gold']} altın)"
            )
        print("0. Geri dön\n")

        choice = input("Almak istediğiniz görev: ").strip()
        if choice == "0":
            return

        try:
            quest_id, quest = available[int(choice) - 1]
        except (ValueError, IndexError):
            print("Geçersiz seçim!")
        else:
            self.active_quests[quest_id] = 0
            print(f"\n✓ '{quest['name']}' görevi alındı!")

        input("Devam etmek için Enter'e basın...")

    def update_quest_progress(self, enemy: Enemy):
        """Advance active quests after a victorious battle"""
        for quest_id in list(self.active_quests):
            quest = QUESTS[quest_id]
            if enemy.enemy_type not in quest["targets"]:
                continue

            progress = self.active_quests[quest_id] + 1
            self.active_quests[quest_id] = progress
            print(
                f"\nGörev ilerlemesi: {quest['name']} "
                f"({progress}/{quest['target_count']})"
            )

            if progress >= quest["target_count"]:
                self.player.add_experience(quest["reward_xp"])
                self.player.gold += quest["reward_gold"]
                self.active_quests.pop(quest_id)
                self.completed_quests.append(quest_id)
                print(
                    f"✓ Görev tamamlandı: {quest['name']}\n"
                    f"+{quest['reward_xp']} XP, +{quest['reward_gold']} altın"
                )

    def store(self):
        """Allow the player to buy equipment and consumables"""
        while True:
            clear_screen()
            print_header("MACERA MAĞAZASI")
            print(f"Altınınız: {self.player.gold}\n")

            catalog = []
            print("SİLAHLAR")
            for key, item in WEAPONS.items():
                catalog.append(("weapon", key, item))
                print(f"{len(catalog)}. {item.name:22} {item.value:3} altın - {item.damage}")

            print("\nZIRHLAR")
            for key, item in ARMOR_ITEMS.items():
                catalog.append(("armor", key, item))
                print(f"{len(catalog)}. {item.name:22} {item.value:3} altın - AC {item.armor_class}")

            print("\nSARF MALZEMELERİ")
            for key, item in CONSUMABLES.items():
                catalog.append(("consumable", key, item))
                print(f"{len(catalog)}. {item.name:22} {item.value:3} altın - {item.description}")

            print("0. Mağazadan çık\n")
            choice = input("Satın almak istediğiniz eşya: ").strip()
            if choice == "0":
                return

            try:
                _, _, item = catalog[int(choice) - 1]
            except (ValueError, IndexError):
                print("Geçersiz seçim!")
                input("Devam etmek için Enter'e basın...")
                continue

            if self.player.gold < item.value:
                print(f"\nYeterli altınınız yok. Gereken: {item.value}")
                input("Devam etmek için Enter'e basın...")
                continue

            item_data = item.to_dict()
            if item.item_type == "consumable":
                existing = next(
                    (owned for owned in self.player.inventory
                     if owned.get("name") == item.name),
                    None,
                )
                if existing:
                    existing["quantity"] = existing.get("quantity", 1) + 1
                else:
                    item_data["quantity"] = 1
                    self.player.inventory.append(item_data)
            else:
                self.player.inventory.append(item_data)

            self.player.gold -= item.value
            print(f"\n✓ {item.name} satın alındı!")
            input("Devam etmek için Enter'e basın...")
    
    def view_character_sheet(self):
        """Display character sheet"""
        clear_screen()
        self.player.display_sheet()

        print("SINIF YETENEĞİ:")
        print("-" * 40)
        print(f"{self.player.character_class.ability_name}")
        print(f"{self.player.character_class.ability_description}\n")
        
        print("BECERİLER:")
        print("-" * 40)
        for skill, bonus in sorted(self.player.skills.items()):
            print(f"{skill:20} {bonus:+3d}")
        
        input("\nDevam etmek için Enter'e basın...")
    
    def view_inventory(self):
        """Display inventory"""
        clear_screen()
        print_header("ENVANTER")
        
        if not self.player.inventory:
            print("Envanteriniz boş.")
        else:
            equipped_weapon = (
                self.player.equipped_weapon.get("name")
                if self.player.equipped_weapon else None
            )
            equipped_armor = (
                self.player.equipped_armor.get("name")
                if self.player.equipped_armor else None
            )

            item_type_names = {
                "weapon": "Silah",
                "armor": "Zırh",
                "consumable": "Sarf malzemesi",
            }

            for index, item in enumerate(self.player.inventory, 1):
                item_type = item_type_names.get(item.get("type"), "Eşya")
                quantity = item.get("quantity", 1)
                quantity_text = f" x{quantity}" if quantity > 1 else ""
                equipped_text = ""

                if item.get("name") == equipped_weapon or item.get("name") == equipped_armor:
                    equipped_text = " [DONANIMLI]"

                print(f"{index}. {item.get('name', 'İsimsiz eşya')}{quantity_text}{equipped_text}")
                print(f"   Tür: {item_type} | Değer: {item.get('value', 0)} altın")

                if item.get("type") == "weapon":
                    print(
                        f"   Hasar: {item.get('damage', '1d4')} "
                        f"({item.get('damage_type', 'bludgeoning')})"
                    )
                elif item.get("type") == "armor":
                    print(f"   Zırh Sınıfı: {item.get('ac', 10)}")
                elif item.get("type") == "consumable":
                    print(f"   Etki: {item.get('description', 'Kullanılabilir eşya')}")
                else:
                    print(f"   {item.get('description', '')}")

                print()
        
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
        save_data["active_quests"] = self.active_quests
        save_data["completed_quests"] = self.completed_quests
        
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
                self.active_quests = {
                    quest_id: int(progress)
                    for quest_id, progress in save_data.get("active_quests", {}).items()
                    if quest_id in QUESTS
                }
                self.completed_quests = [
                    quest_id
                    for quest_id in save_data.get("completed_quests", [])
                    if quest_id in QUESTS
                ]
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
