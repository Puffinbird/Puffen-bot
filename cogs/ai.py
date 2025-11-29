# ==================== AI.PY ====================
import discord
from discord.ext import commands
from discord import app_commands
import requests, os, logging
from logging.handlers import RotatingFileHandler
from cogs.utils_core import send_temp

os.makedirs("logs", exist_ok=True)

guild_logger = logging.getLogger("guild_ai")
guild_handler = RotatingFileHandler("logs/guild_ai.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
guild_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
guild_logger.addHandler(guild_handler)
guild_logger.setLevel(logging.INFO)

def ask_local_ai(prompt: str) -> str:
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        return response.json()["response"].strip()
    except Exception as e:
        return f"⚠️ Fel vid kontakt med lokal AI: {e}"

class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="askai", description="Fråga den lokala AI:n något")
    async def askai(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        answer = ask_local_ai(prompt)

        guild_name = interaction.guild.name if interaction.guild else "DM"
        guild_logger.info(f"{interaction.user} frågade i {guild_name}: {prompt}")
        guild_logger.info(f"AI svarade: {answer}")

        # ✂️ Dela upp svaret i bitar med etikett
        chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
        total = len(chunks)

        for i, chunk in enumerate(chunks, start=1):
            label = f"(del {i}/{total})"
            await send_temp(interaction.followup, f"🤖 {label}\n{chunk}", is_ai=True)



async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
