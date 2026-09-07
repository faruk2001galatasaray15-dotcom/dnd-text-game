# D&D Text Game 🐉

Tamamıyla metin tabanlı, D&D 5e mekaniklerine sahip tek oyunculu bilgisayar oyunu.

## Özellikleri

✨ **D&D 5e Mekaniklerine Uygun**
- Doğru zarlar sistemi (d20, d12, d10, d8, d6, d4)
- Ability scores ve modifiers
- Advantage/Disadvantage sistemi
- Saving throws ve skill checks

⚔️ **Dinamik Savaş Sistemi**
- Turn-based combat
- Realistic initiative system
- Attack rolls with modifiers
- Damage calculations with crits
- Health tracking

🏰 **Derinlemesine Dünya**
- Procedurally generated encounters
- NPC interactions
- Inventory management
- Equipment system

💾 **Oyun Kaydetme/Yükleme**
- JSON tabanlı save system
- Multiple save slots
- Character progression

## Kurulum

```bash
# Repoyu klonla
git clone https://github.com/faruk2001galatasaray15-dotcom/dnd-text-game.git
cd dnd-text-game

# (Opsiyonel) Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Oyunu başlat
python main.py
```

## Kullanım

```bash
python main.py
```

Oyunda yer alan komutları takip edin ve maceraya başlayın!

## Oyun Akışı

1. **Karakter Oluşturma** - Karakterinizi tanımlayın (sınıf, ırk, ability scores)
2. **Macera** - Dungeons, encounters ve NPCler ile karşılaşın
3. **Savaş** - D&D 5e kurallarına uygun turnlara dayalı combat
4. **Gelişim** - XP kazanın ve level atın

## Teknik Detaylar

- **Dil**: Python 3.8+
- **Dependencies**: Yalnızca Python standard library
- **Mimari**: Object-oriented design
- **Save Format**: JSON

## Dosya Yapısı

```
dnd-text-game/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              # Bu dosya
├── game/
│   ├── __init__.py
│   ├── game.py            # Main game loop
│   ├── character.py       # Character class
│   ├── combat.py          # Combat system
│   ├── dice.py            # Dice rolling
│   └── utils.py           # Helper functions
└── data/
    ├── saves/             # Save files
    └── encounters.json    # Encounter definitions
```

## Lisans

MIT License - Özgürce kullan ve değiştir!

## Kontribüsyon

Pull requestler memnuniyetle karşılanır! Büyük değişiklikler için lütfen önce bir issue açın.

## Yol Haritası

- [ ] Complete character creation system
- [ ] Basic dungeon exploration
- [ ] Combat system implementation
- [ ] NPC dialogue system
- [ ] Quest system
- [ ] Experience and leveling
- [ ] Advanced combat features (spells, abilities)
- [ ] Multiplayer support (future)

## İletişim

Sorular veya öneriler için issue açın!

---

**Eğlenceli maceralar! 🗡️**
