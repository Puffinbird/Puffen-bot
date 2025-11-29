# ==================== CONFIG.PY ====================
import os

class BotConfig:
    def __init__(self):
        self.name = "→ ᴘᴜꜰꜰᴇɴ ←"
        self.version = "1.0.0"
        self.status = self._funny_status()

    def _funny_status(self):
        """Returnerar ett slumpmässigt roligt statusmeddelande"""
        from random import choice
        return choice([
            "Counting puffins 🐧",
            "Sniffing server logs 👃",
            "Judging your slash commands ⚖️",
            "Watching memes evolve 📈",
            "Debugging reality itself 🧠",
            "Waiting for !help like a champ 🏆",
            "Plotting world domination... with emojis 😈",
        ])

config = BotConfig()
