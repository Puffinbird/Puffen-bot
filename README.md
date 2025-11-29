# 🐧 Puffin Discord Bot

En modulär och kraftfull Discord-bot byggd med `discord.py` och cogs-systemet. Puffin är utformad för att vara enkel att använda, enkelt att utöka och stabil i långsiktig drift.

---

## ✨ Funktioner

### 🎮 Spel & Underhållning
- **Spel**: `!ping`, `!cf` (slantsingling), `!rps` (sten-sax-påse), `!roll` (tärning), `!8ball` (magisk boll)
- **Citat**: Lägg till, visa och hantera servercitat med författare och datum

### 📊 Statistik & Aktivitet
- **Aktivitetsräkning**: Spårar meddelanden per användare och server
- **Topplista**: Visar mest aktiva medlemmar
- **Backfill**: Läs in historiska meddelanden för analys
- **Exportera**: Hämta statistik i JSON-format

### 👤 Rollhantering
- **Reaktionsroller**: Användare kan få roller genom att reagera på meddelanden
- **Rollmeny**: Interaktiv rollmeny för enkel rollhantering
- **Anpassningsbar**: Lätt att lägga till nya roller

### 🤖 AI-integration
- **Slash-commands**: `/askai` för AI-frågor i kanaler
- **Direct Messages**: Chatta med AI:n direkt i DM
- **Loggning**: Alla AI-samtal sparas separat för granskning
- **Context-medveten**: Boten förstår sammanhanget i konversationer

### 🔧 Admin & Verktyg
- **Synkronisering**: `/sync` för att synkronisera slash-commands
- **Loggning**: Detaljerad loggning av kommandon, fel och händelser
- **Tillfälliga svar**: Automatisk borttagning av botens svar efter viss tid
- **Fel-hantering**: Robust fel-hantering med logging

### ❓ Hjälp
- **Eget hjälpkommando**: `!help` visar alla tillgängliga kommandon
- **Kategoriserat**: Kommandon grupperade efter typ
- **Detaljerat**: Varje kommando har beskrivning och användning

---

## 📋 Krav

- **Python 3.13+**
- **Discord-server** där du är moderator
- **Discord Application Token** från [Discord Developer Portal](https://discord.com/developers/applications)
- **OpenAI API-nyckel** (valfritt, för AI-funktioner) från [OpenAI](https://platform.openai.com/)

---

## 📦 Installation

### 1. Klona projektet
```bash
git clone https://github.com/dittrepo/puffin-bot.git
cd puffin-bot
```

### 2. Skapa och aktivera virtual environment
```bash
python3.13 -m venv venv
source venv/bin/activate
```

### 3. Installera alla beroenden
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Skapa `.env`-fil
Skapa en fil med namn `.env` i projektets rot och lägg till:

```env
# Discord Bot Token (från Developer Portal)
DISCORD_TOKEN=your_token_here

# OpenAI API Key (för AI-funktioner)
OPENAI_API_KEY=your_openai_key_here

# Valfritt: Discord Server ID för testing
GUILD_ID=your_guild_id_here
```

**Viktigt**: Lägg till `.env` i `.gitignore` så att du inte commitar känslig information!

### 5. Verifiera mappstruktur
```
puffin-bot/
├── main.py                    # Huvudfil
├── config.json                # Bot-konfiguration
├── requirements.txt           # Python-beroenden
├── update.sh                  # Start- och uppdaterings-skript
├── .env                       # Miljövariabler (GITIGNORE!)
├── .gitignore
├── README.md
├── cogs/                      # Bot-moduler
│   ├── activity.py            # Aktivitetsräkning
│   ├── admin.py               # Admin-kommandon
│   ├── ai.py                  # AI-integration
│   ├── fun.py                 # Spel och underhållning
│   ├── help.py                # Hjälpkommando
│   ├── quotes.py              # Citathantering
│   ├── roles.py               # Rollhantering
│   ├── sync.py                # Slash-command synk
│   └── utils_core.py          # Hjälpfunktioner
├── data/                      # Serverspesifik data (JSON)
│   ├── activity_*.json
│   ├── quotes_*.json
│   ├── reaction_roles_*.json
│   └── role_menu_*.json
├── logs/                      # Loggfiler
│   ├── commands.log
│   ├── errors.log
│   ├── dm_ai.log
│   └── guild_ai.log
└── venv/                      # Virtual environment
```

---

## 🚀 Starta botten

### Enkelt sätt (utveckling)
```bash
source venv/bin/activate
python3 main.py
```

### Med update-skriptet (rekommenderat för produktion)
```bash
bash update.sh
```

Detta skriptet:
- Uppdaterar alla beroenden
- Stänger ned tidigare instanser
- Startar boten i bakgrunden med `nohup`
- Sparar loggar till `bot.log`
- Lagrar process ID för enkel stopp

---

## 📋 Användbara kommandon

### 🎮 Användarkommandon
| Kommando | Beskrivning |
|----------|-------------|
| `!ping` | Visa latens |
| `!cf` | Slantsingling |
| `!rps [rock/paper/scissors]` | Sten-sax-påse |
| `!roll [sidor]` | Kasta tärning (standard: d20) |
| `!8ball` | Magisk boll |
| `!quote [add/show/remove]` | Hantera citat |
| `!help` | Visa alla kommandon |
| `/askai <fråga>` | Fråga AI:n |

### 🔧 Admin-kommandon
| Kommando | Beskrivning |
|----------|-------------|
| `/sync` | Synkronisera slash-commands |
| `!stats` | Visa aktivitetsstatistik |
| `!backfill` | Läs in historiska meddelanden |
| `!export_stats` | Exportera statistik till JSON |

---

## 🛠️ Server-drift

### Visa live-loggar
```bash
tail -f /home/linus/Puffen-bot/bot.log
```

### Kontrollera om boten körs
```bash
ps aux | grep main.py
```

### Stoppa boten
```bash
kill $(cat /home/linus/Puffen-bot/bot.pid)
```

### Starta om boten
```bash
bash /home/linus/Puffen-bot/update.sh
```

### Kolla begränsningar och status
```bash
# Se om boten har de nödvändiga behörigheterna
curl -H "Authorization: Bot YOUR_TOKEN" https://discord.com/api/v10/users/@me
```

---

## ⚙️ Konfiguration

### `config.json`
Redigera bot-inställningar här:
```json
{
  "prefix": "!",
  "delete_temp_messages": true,
  "temp_message_delay": 30,
  "max_quote_length": 2000,
  "activity": "Watching over servers"
}
```

### `.env`
Miljövariabler för känslig information:
```env
DISCORD_TOKEN=token_här
OPENAI_API_KEY=key_här
```

---

## 🔐 Säkerhet

- **Håll `.env` privat**: Lägg ALDRIG till `.env` i Git
- **Begränsad åtkomst**: Vissa kommandon kräver moderator-behörigheter
- **Loggning**: Alla AI-samtal och kommandon loggas för granskning
- **Rate-limiting**: Boten respekterar Discord API-gränser

---

## 📝 Loggning

Botten loggar aktivitet i tre nivåer:

- **INFO**: Normala operationer och kommandoanvändning
- **WARNING**: Oväntade situationer som kan påverka drift
- **ERROR**: Fel som behöver uppmärksammas

Loggar sparas i:
- `logs/commands.log` - Alla användarkommandon
- `logs/errors.log` - Fel och avvikelser
- `logs/dm_ai.log` - DM-konversationer med AI
- `logs/guild_ai.log` - Guild-konversationer med AI

---

## 🐛 Felsökning

### Boten startar inte
```bash
# Kontrollera att virtual environment är aktiverat
source venv/bin/activate

# Kontrollera att alla beroenden är installerade
pip install -r requirements.txt

# Kolla loggarna
cat bot.log
```

### "Token is invalid"
- Verifiera att `DISCORD_TOKEN` är korrekt i `.env`
- Generera en ny token från [Developer Portal](https://discord.com/developers/applications)
- Se till att boten har de nödvändiga behörigheterna

### AI-kommandon fungerar inte
- Kontrollera att `OPENAI_API_KEY` är inställd i `.env`
- Verifiera att du har tillräckliga krediter hos OpenAI
- Kolla `logs/errors.log` för felmeddelanden

### Boten svarar inte på kommandon
- Kontrollera att boten är online i Discord
- Se till att boten har `Send Messages` och `Read Messages` behörigheter
- Försök `/sync` för att uppdatera slash-commands
- Kolla `logs/commands.log` för kommandohistorik

---

## 📚 Utöka botten

### Lägga till en ny cog (modul)

1. Skapa en ny fil i `cogs/` mappen:
```python
# cogs/my_feature.py
import discord
from discord.ext import commands

class MyFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mycommand(self, ctx):
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(MyFeature(bot))
```

2. Cogen laddas automatiskt från `main.py`

---

## 🤝 Bidra

Vill du förbättra Puffin? Följ dessa steg:

1. Fork projektet
2. Skapa en feature-branch (`git checkout -b feature/AmazingFeature`)
3. Commit dina ändringar (`git commit -m 'Add AmazingFeature'`)
4. Push till branchen (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request

---

## 📄 Licens

Detta projekt är licensierat under MIT-licensen. Se `LICENSE`-filen för detaljer.

---

## 🙋 Support

Har du frågor eller problem?

- 📖 Läs [Discord.py dokumentation](https://discordpy.readthedocs.io/)
- 🐛 Öppna ett [GitHub Issue](https://github.com/dittrepo/puffin-bot/issues)
- 💬 Kontakta mig på Discord

---

## 📈 Status & Todo

- [x] Grundläggande bot-struktur
- [x] Spel och underhållning
- [x] Aktivitetsräkning och statistik
- [x] AI-integration
- [x] Rollhantering
- [x] Loggning
- [ ] Databaskoppling för större servrar
- [ ] Webpanel för admin
- [ ] Musik-spelare

---

**Gjord med ❤️ för Discord-communityn**