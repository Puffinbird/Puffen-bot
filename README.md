# Puffin Discord Bot 🐧

En modulär Discord‑bot byggd med `discord.py` och cogs.
Botten innehåller spelkommandon, statistik, rollmeny, AI‑svar, och ett eget hjälpkommando.

---

## 🚀 Funktioner

- **Spel**: `!ping`, `!cf`, `!rps`, `!roll`, `!8ball`
- **Statistik**: Räknar meddelanden per användare, visar topplista, kan backfilla gamla meddelanden
- **Roller**: Rollmeny med reaktionsroller
- **Citat**: Lägg till, visa och ta bort citat med datum och författare
- **AI**: Fråga AI:n via `/askai` eller direkt i DM
- **Hjälp**: Eget hjälpkommando med översikt över alla funktioner
- **Tillfälliga meddelanden**: Alla svar raderas automatiskt efter en viss tid (via `utils.send_temp`)
- **Loggning**: Kommandon, fel och AI‑samtal loggas separat i `logs/`

---

## 📦 Installation

1. Klona projektet:
    ```bash
    git clone https://github.com/dittrepo/puffin-bot.git
    cd puffin-bot
    ```

2. Installera beroenden:
    ```bash
    pip install -U discord.py python-dotenv openai
    ```

3. Skapa en `.env`‑fil i projektets rot:
    ```
    TOKEN=din_discord_token_här
    OPENAI_API_KEY=din_openai_nyckel_här
    ```

4. Mappstruktur:
    ```
    puffin-bot/
    ├── main.py
    ├── config.json
    ├── README.md
    ├── .env
    ├── cogs/
    │   ├── activity.py
    │   ├── admin.py
    │   ├── ai.py
    │   ├── fun.py
    │   ├── help.py
    │   ├── quotes.py
    │   ├── roles.py
    │   ├── sync.py
    │   └── utils_core.py
    ├── data/
    │   ├── activity_<guild_id>.json
    │   ├── quotes_<guild_id>.json
    │   ├── reaction_roles_<guild_id>.json
    │   └── role_menu_<guild_id>.json
    ├── logs/
    │   ├── commands.log
    │   ├── errors.log
    │   ├── dm_ai.log
    │   └── guild_ai.log
    └── venv/ (valfri virtuell miljö)
    ```

5. Starta boten:
    ```bash
    python main.py
    ```

---

## ⚙️ Tips

- **Token**: Håll din Discord‑token hemlig, dela den aldrig offentligt.
- **Rollmeny**: Uppdatera `ROLE_MENU_MESSAGE_ID` i `roles.py` när du skapar en ny rollmeny.
- **Statistik**: Meddelanden sparas i `data/activity_<guild_id>.json`. Filen uppdateras automatiskt.
- **Citat**: Alla citat sparas per guild i `data/quotes_<guild_id>.json`.
- **AI**: Frågor via `/askai` loggas i `logs/guild_ai.log`, DM‑samtal i `logs/dm_ai.log`.
- **Loggar**: Alla loggar roteras automatiskt vid 5 MB. Du hittar dem i `logs/`.

---

## 🧩 Utbyggnad

Lägg till fler cogs i `cogs/` och ladda dem via `main.py`.
Alla cogs är modulära och kan enkelt utökas med nya kommandon eller funktioner.
