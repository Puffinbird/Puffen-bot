# 🎲 Puffen-RPG Discord Bot

En komplett D&D 5e bot för Discord med karaktärshantering, strid, spells, NPCs, monsters och mycket mer!

## 📁 Filstruktur

```
dnd_bot/
├── main.py              # Huvudfil som startar boten
├── config.py            # Konfiguration och konstanter
├── requirements.txt     # Python dependencies
├── README.md            # Denna fil
├── cogs/
│   ├── __init__.py      # Tom fil (behövs för Python)
│   ├── dice.py          # Tärningskommandon
│   ├── character.py     # Karaktärshantering
│   ├── combat.py        # Stridsystem
│   ├── spells.py        # Spell tracking
│   ├── gm.py            # GM-kommandon, NPCs, Monsters
│   ├── shop.py          # Item shop och trading
│   ├── quests.py        # Quest tracking
│   ├── loot.py          # Loot tables och treasure
│   └── help.py          # Hjälpkommandon
└── data/
    └── dnd_data.json    # (Skapas automatiskt) Sparad data
```

## 🚀 Installation

### 1. Förberedelser

```bash
# Klona eller skapa projektmappen
mkdir dnd_bot
cd dnd_bot

# Skapa alla mappar
mkdir cogs data
```

### 2. Skapa alla filer

Kopiera innehållet från varje fil (se artifacts) och skapa:
- `main.py`
- `config.py`
- `requirements.txt`
- `README.md`
- `cogs/__init__.py` (tom fil)
- `cogs/dice.py`
- `cogs/character.py`
- `cogs/combat.py`
- `cogs/spells.py`
- `cogs/gm.py`
- `cogs/shop.py`
- `cogs/quests.py`
- `cogs/loot.py`
- `cogs/help.py`

### 3. Lägg till bot token i miljön

Lägg till detta i din `.bashrc` eller `.zshrc`:

```bash
export PUFFEN_RPG_TOKEN="din_bot_token_här"
```

Ladda om din shell:
```bash
source ~/.bashrc  # eller source ~/.zshrc
```

### 4. Installera dependencies

```bash
pip install -r requirements.txt
```

### 5. Starta boten

```bash
python main.py
```

## 🎮 Kommandon

### 🎲 Tärningar
- `/roll <dice>` - Slå tärningar (t.ex. 1d20, 2d6+3, 1d20adv, 1d20dis)
- `/stats` - Slå karaktärsstats (4d6 drop lowest)
- `/coinflip` - Kasta ett mynt

### ⚔️ Karaktärer
- `/createchar` - Skapa din karaktär med alla stats
- `/char [target]` - Visa karaktär (din eller någon annans)
- `/deletechar` - Ta bort din karaktär
- `/additem` - Lägg till vapen, rustning, consumables, etc.
- `/inventory [target]` - Visa inventory

### ⚔️ Strid
- `/initiative` - Slå initiative för strid
- `/attack [target]` - Attackera med ditt vapen
- `/heal <amount> [target]` - Heala dig själv eller någon annan
- `/addcondition <condition> [target]` - Lägg till condition (Poisoned, Stunned, etc.)
- `/removecondition <condition> [target]` - Ta bort condition
- `/conditions` - Visa alla tillgängliga D&D conditions
- `/temphp <amount> [target]` - Lägg till temporary HP

### ✨ Spells (Spellcasters)
- `/addspell <name> <level>` - Lägg till en spell till din spellbook
- `/spellbook [target]` - Visa alla dina spells
- `/cast <spell_name> [level]` - Casta en spell (använder spell slot)
- `/longrest` - Ta en long rest (återställ HP och spell slots)
- `/shortrest [hit_dice]` - Ta en short rest (slå hit dice för healing)

### 🏪 Shop & Trading
- `/shop [category]` - Visa shop med alla items (vapen, rustning, potions, etc.)
- `/buy <item> [quantity]` - Köp items från shoppen
- `/sell <item>` - Sälj items för 50% av priset
- `/use <item> [target]` - Använd consumables (healing potions, etc.)
- `/trade <target> <item> [gold]` - Tradea items eller guld med andra spelare

### 📜 Quests
- `/quests [filter]` - Visa alla quests (All/Available/Active/Completed)
- `/myquests` - Visa dina aktiva quests med progress
- `/acceptquest <n>` - Acceptera en quest
- `/abandonquest <n>` - Avbryt en quest

### 🎁 Loot & Treasure
- `/opentreasure <n>` - Öppna en treasure chest

### 🎮 GM Kommandon (Admin)
**Spelarna:**
- `/party` - Visa alla karaktärer i gruppen
- `/damage <target> <amount>` - Ge skada till en spelare
- `/sethp <target> <hp>` - Sätt HP för en spelare
- `/givexp <target> <xp>` - Ge XP till en spelare
- `/givegold <target> <gold>` - Ge guld till en spelare
- `/giveitem <target> <name>` - Ge item till en spelare

**NPCs & Monsters:**
- `/createnpc <name>` - Skapa en NPC
- `/createmonster <name>` - Skapa ett monster
- `/npcs` - Visa alla NPCs
- `/monsters` - Visa alla monsters
- `/damagenpc <name> <amount>` - Ge skada till NPC/monster
- `/deletenpc <name>` - Ta bort en NPC
- `/deletemonster <name>` - Ta bort ett monster

### 📖 Hjälp
- `/help` - Visa alla kommandon
- `/guide` - Steg för steg guide för att spela

## 🎯 Features

✅ **Komplett Karaktärssystem**
- Alla 6 D&D stats (STR, DEX, CON, INT, WIS, CHA)
- 12 olika klasser (Fighter, Wizard, Rogue, etc.)
- HP tracking med visual HP bar
- AC (Armor Class) och Proficiency bonus
- Inventory system med vapen, rustning, consumables
- Level och XP tracking
- Gold/valuta system

✅ **Avancerat Stridssystem**
- Initiative rolls
- Attack rolls med auto-beräkning (stat modifiers + proficiency)
- Damage rolls med critical hits
- Advantage/Disadvantage på tärningsslag
- Temporary HP system
- D&D Conditions (Poisoned, Stunned, Paralyzed, etc.)

✅ **Spell System** (för spellcasters)
- Spellbook med alla dina spells
- Spell slots tracking per level
- Auto-beräkning av spell slots baserat på karaktärslevel
- Long rest och short rest
- Cantrips (använder inga spell slots)

✅ **GM Tools**
- Skapa och hantera NPCs
- Skapa och hantera Monsters med stats
- Ge/ta skada från spelare och NPCs
- Ge XP, guld och items
- Visa hela party med HP bars och stats
- Quest system med objectives och rewards
- Loot tables med 5 rarity levels
- Monster-specific loot generation
- Treasure chests som spelare kan hitta

✅ **Shop & Economy**
- 20+ items i shoppen (vapen, rustning, potions)
- Köp och sälj items
- Trading mellan spelare
- Använd consumables (healing potions, antidotes)
- Item rarity system

✅ **Quest System**
- GM skapar quests med descriptions och rewards
- Multi-objective quest tracking
- Quest progress tracking för varje spelare
- XP och gold rewards vid completion
- Quest status (Available/Active/Completed)

✅ **Loot System**
- 5 rarity levels (Common, Uncommon, Rare, Epic, Legendary)
- Weighted random loot generation
- Monster-specific loot tables
- Treasure chests för hidden loot
- Party-wide loot distribution
- Auto-scaling loot baserat på monster

✅ **Smart Datahantering**
- All data sparas automatiskt i JSON
- Karaktärer är serverbaserade (olika servrar = olika karaktärer)
- Inget data förloras vid restart

## 💡 Tips & Tricks

- **Advantage/Disadvantage**: Använd `1d20adv` eller `1d20dis` i `/roll`
- **Spellcasters**: Kom ihåg att använda `/addspell` efter att du skapat din karaktär
- **Party Overview**: GM kan använda `/party` för att se alla spelares HP och status
- **Conditions**: Använd `/conditions` för att se alla tillgängliga D&D conditions
- **Long Rest**: Använd `/longrest` för att återställa allt (HP, spell slots, conditions)
- **Shop Smart**: Köp healing potions innan äventyr! Använd `/shop Consumable` för snabb access
- **Quest Tracking**: Använd `/myquests` för att se dina aktiva quests med progress
- **Loot Tables**: GMs, använd `/loottable Epic` för att se vilken loot som kan dropp från epic encounters
- **Monster Loot**: Efter strid, använd `/monsterloot Goblin @Spelare` för automatisk loot
- **Treasure Hunting**: GMs kan placera treasure chests med `/treasure` som spelare hittar och öppnar

## 🔧 Tekniska Detaljer

- **Språk**: Python 3.8+
- **Library**: discord.py 2.3+
- **Data Storage**: JSON fil-baserad lagring
- **Bot Type**: Slash commands (moderna Discord commands)

## 📝 Exempel på Användning

### Skapa en karaktär:
```
1. /stats                    (slå karaktärsstats)
2. /createchar name:Thorin class:Fighter level:1 strength:16 dexterity:12 ...
3. /additem name:Longsword item_type:Weapon damage:1d8
4. /char                     (visa din karaktär)
```

### Strid med loot:
```
1. GM: /createmonster name:Goblin hp:7 ac:15 attack_bonus:4 damage:1d6+2
2. Alla: /initiative         (alla slår initiative)
3. Spelare: /attack Goblin   (attackera monstret)
4. GM: /damage @Spelare 5    (ge skada till spelare)
5. Spelare: /use "Healing Potion"  (använd potion)
6. GM: /monsterloot Goblin @Spelare  (ge loot efter strid)
```

### Quest system:
```
1. GM: /createquest name:"Slay the Dragon" description:"..." xp_reward:1000 gold_reward:500
2. GM: /addobjective quest:"Slay the Dragon" objective:"Find the dragon's lair"
3. Spelare: /acceptquest "Slay the Dragon"
4. Spelare: /myquests  (se progress)
5. GM: /completeobjective quest:"Slay the Dragon" objective_number:1
6. GM: /completequest quest:"Slay the Dragon" player:@Spelare
```

### Shopping:
```
1. Spelare: /shop Weapon      (se alla vapen)
2. Spelare: /buy Longsword    (köp svärd)
3. Spelare: /buy "Healing Potion" quantity:3
4. Spelare: /trade @Friend "Healing Potion" gold_amount:10
```

## 🐛 Felsökning

**Bot startar inte:**
- Kontrollera att `PUFFEN_RPG_TOKEN` är satt i miljön: `echo $PUFFEN_RPG_TOKEN`
- Kontrollera att alla dependencies är installerade: `pip install -r requirements.txt`

**Slash commands syns inte:**
- Vänta 1-2 minuter efter bot start (Discord synkar commands)
- Kontrollera att boten har rätt permissions i servern
- Prova `/sync` kommandot (endast bot owner)

**Data sparas inte:**
- Kontrollera att `data/` mappen finns
- Kontrollera write-permissions på mappen

## 📜 Licens

Fri att använda för egna projekt!

## 🎲 Ha kul och spela D&D!

Roll for initiative! 🎲⚔️