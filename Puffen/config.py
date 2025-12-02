# ==================== CONFIG.PY ====================
import json, os, random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class BotConfig:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.name = data["bot"]["name"]
        self.version = data["bot"]["version"]
        self.status = data["bot"].get("status") or self._funny_status()
        self.logging = data.get("logging", {})
        self.xp = data.get("xp", {})
        self.timeouts = data.get("timeouts", {})
        self.limits = data.get("limits", {})

    def _funny_status(self):
        return random.choice([
            "Counting puffins 🐧",
            "Sniffing server logs 👃",
            "Judging your slash commands ⚖️",
            "Watching memes evolve 📈",
            "Debugging reality itself 🧠",
            "Plotting world domination... with emojis 😈",
        ])

config = BotConfig()
