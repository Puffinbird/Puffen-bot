# 🎲 Puffen-RPG - Komplett Installationsguide

## 📋 Checklist

Alla filer du behöver skapa:

### Huvudfiler:
- [ ] `main.py` - Startar boten
- [ ] `config.py` - Konfiguration
- [ ] `requirements.txt` - Dependencies
- [ ] `README.md` - Dokumentation

### Cogs (alla i `cogs/` mappen):
- [ ] `cogs/__init__.py` - Tom fil
- [ ] `cogs/dice.py` - Tärningar
- [ ] `cogs/character.py` - Karaktärer
- [ ] `cogs/combat.py` - Strid
- [ ] `cogs/spells.py` - Spells
- [ ] `cogs/gm.py` - GM tools, NPCs, Monsters
- [ ] `cogs/shop.py` - **NYA!** Shop och trading
- [ ] `cogs/quests.py` - **NYA!** Quest system
- [ ] `cogs/loot.py` - **NYA!** Loot tables
- [ ] `cogs/help.py` - Hjälp (uppdaterad)

## 🚀 Steg-för-steg Installation

### Steg 1: Skapa projektstruktur

```bash
# Skapa huvudmapp
mkdir dnd_bot
cd dnd_bot

# Skapa undermappar
mkdir cogs data
```

### Steg 2: Lägg till bot token i miljön

Öppna din `.bashrc` eller `.zshrc`:

```bash
nano ~/.bashrc
```

Lägg till denna rad i slutet:

```bash
export PUFFEN_RPG_TOKEN="din_discord_bot_token_här"
```

Spara och ladda om:

```bash
source ~/.bashrc
```

Verifiera att token är satt:

```bash
echo $PUFFEN_RPG_TOKEN
```

### Steg 3: Skapa alla filer

Kopiera innehållet från varje artifact och skapa filerna:

#### Huvudfiler:

**main.py**
```bash
touch main.py
nano main.py
# Klistra in innehållet från artifact: "main.py - Puffen-RPG Bot"
```

**config.py**
```bash
touch config.py
nano config.py
# Klistra in innehållet från artifact: "config.py - Konfiguration"
```

**requirements.txt**
```bash
touch requirements.txt
nano requirements.txt
# Klistra in innehållet från artifact: "requirements.txt"
```

**README.md**
```bash
touch README.md
nano README.md
# Klistra in innehållet från artifact: "README.md"
```

#### Cogs filer:

```bash
# Skapa tom __init__.py
touch cogs/__init__.py

# Skapa alla cog filer
touch cogs/dice.py
touch cogs/character.py
touch cogs/combat.py
touch cogs/spells.py
touch cogs/gm.py
touch cogs/shop.py
touch cogs/quests.py
touch cogs/loot.py
touch cogs/help.py
```

Redigera varje fil och klistra in innehållet från motsvarande artifact.

### Steg 4: Installera Python dependencies

```bash
pip install -r requirements.txt
```

Eller om du använder pip3:

```bash
pip3 install -r requirements.txt
```

### Steg 5: Starta boten

```bash
python main.py
```

Eller:

```bash
python3 main.py
```

Du borde se:

```
🔄 Laddar cogs...
✅ Laddade cogs.dice
✅ Laddade cogs.character
✅ Laddade cogs.combat
✅ Laddade cogs.spells
✅ Laddade cogs.gm
✅ Laddade cogs.shop
✅ Laddade cogs.quests
✅ Laddade cogs.loot
✅ Laddade cogs.help
🔄 Synkar slash commands...
✅ Slash commands synkade!

==================================================
🎲 Puffen-RPG är online!
📛 Namn: YourBotName
🆔 ID: 123456789
🌐 Servrar: 1
==================================================
```

## 🎮 Första användning

### 1. Bjud in boten till din server

Skapa en invite link i Discord Developer Portal med följande permissions:
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History
- Add Reactions

### 2. Testa grundläggande kommandon

```
/help          # Se alla kommandon
/roll 1d20     # Slå en tärning
/createchar    # Skapa din första karaktär
/shop          # Visa shoppen
/quests        # Se tillgängliga quests
```

### 3. GM Setup (Admin)

Som admin, testa:

```
/createmonster name:Goblin hp:7 ac:15
/createquest name:"First Quest" description:"Test quest" xp_reward:100
/loot Common   # Generera loot
```

## 📦 Nya Features (version 2.0)

### 🏪 Shop System

- 20+ items att köpa (vapen, rustning, potions)
- Köp och sälj system
- Trading mellan spelare
- Använd consumables för healing

**Exempel:**
```
/shop Weapon
/buy Longsword
/use "Healing Potion"
/trade @Friend "Healing Potion" gold_amount:10
```

### 📜 Quest System

- GM skapar quests med objectives
- Spelare kan acceptera och tracka quests
- Progress tracking med checkboxes
- XP och gold rewards

**Exempel:**
```
GM: /createquest name:"Slay Goblins" xp_reward:500
GM: /addobjective quest:"Slay Goblins" objective:"Kill 10 goblins"
Spelare: /acceptquest "Slay Goblins"
Spelare: /myquests
```

### 🎁 Loot System

- 5 rarity levels (Common → Legendary)
- Monster-specific loot
- Treasure chests
- Party-wide loot distribution

**Exempel:**
```
GM: /loot Rare 3 @Spelare
GM: /monsterloot Dragon @Spelare
GM: /rollloot Epic  # Loot till hela party
GM: /treasure name:"Ancient Chest" gold:500
```

## 🔧 Felsökning

### Problem: Bot startar inte

**Lösning:**
```bash
# Kontrollera token
echo $PUFFEN_RPG_TOKEN

# Om tomt, lägg till i bashrc
export PUFFEN_RPG_TOKEN="din_token"
source ~/.bashrc
```

### Problem: Slash commands syns inte

**Lösning:**
- Vänta 1-2 minuter (Discord synkar)
- Kicka och bjud in boten igen
- Kontrollera bot permissions

### Problem: Import errors

**Lösning:**
```bash
# Installera om dependencies
pip install --upgrade discord.py
```

### Problem: Data sparas inte

**Lösning:**
```bash
# Kontrollera att data mappen finns
mkdir -p data

# Kontrollera permissions
chmod 755 data
```

## 📊 Filstorlek

Total storlek: ~25 KB Python kod

- main.py: ~1.5 KB
- config.py: ~1.5 KB
- dice.py: ~2 KB
- character.py: ~4 KB
- combat.py: ~3.5 KB
- spells.py: ~4 KB
- gm.py: ~5 KB
- shop.py: ~4.5 KB
- quests.py: ~5 KB
- loot.py: ~6 KB
- help.py: ~2 KB

## ✅ Verifiering

Kontrollera att allt fungerar:

```bash
# 1. Kolla att alla filer finns
ls -la
ls -la cogs/

# 2. Kolla Python syntax
python -m py_compile main.py
python -m py_compile cogs/*.py

# 3. Starta bot
python main.py
```

## 🎉 Klart!

Din Puffen-RPG bot är nu helt installerad med:
- ✅ Komplett D&D 5e system
- ✅ Karaktärer och strid
- ✅ Spells och spell slots
- ✅ NPCs och Monsters
- ✅ Shop och trading
- ✅ Quest system
- ✅ Loot tables och treasure

Använd `/help` i Discord för att se alla kommandon!

## 📞 Support

Problem? Kontrollera:
1. README.md för användning
2. Alla filer är skapade korrekt
3. Token är satt i miljön
4. Python 3.8+ är installerat
5. discord.py är installerat

Happy adventuring! 🎲⚔️