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
DATA_FOLDER = './data'
DATA_FILE = f'{DATA_FOLDER}/dnd_data.json'

# Skapa data folder om den inte finns
os.makedirs(DATA_FOLDER, exist_ok=True)