# ============================================
# FILE: config.py
# ============================================
import os
from dotenv import load_dotenv

# Ladda .env fil om den finns
load_dotenv()

# Bot Token - ÄNDRA DETTA!
TOKEN = os.getenv('DISCORD_TOKEN', 'DIN_BOT_TOKEN_HÄR')

# Prefix för textkommandon (används mest för debug)
PREFIX = '!'

# Data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_FOLDER, "dnd_data.json")

# Skapa data folder om den inte finns
os.makedirs(DATA_FOLDER, exist_ok=True)

# D&D 5e Conditions
CONDITIONS = [
    "Blinded",
    "Charmed",
    "Deafened",
    "Frightened",
    "Grappled",
    "Incapacitated",
    "Invisible",
    "Paralyzed",
    "Petrified",
    "Poisoned",
    "Prone",
    "Restrained",
    "Stunned",
    "Unconscious",
    "Exhaustion"
]
