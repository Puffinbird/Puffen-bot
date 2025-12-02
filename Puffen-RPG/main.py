import discord
from discord.ext import commands
import asyncio
import os
import logging

# 📁 Basmapp för projektet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COGS_DIR = os.path.join(BASE_DIR, "cogs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 📝 Skapa loggmapp om den saknas
os.makedirs(LOGS_DIR, exist_ok=True)

# 🧠 Botnamn och token
BOT_NAME = "Puffen-RPG"
TOKEN = os.getenv(f"{BOT_NAME.upper().replace('-', '_')}_TOKEN")
if not TOKEN:
    raise RuntimeError(f"❌ TOKEN för {BOT_NAME} saknas i miljön")

# 🔔 Loggning till fil
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(message)s"
)
logger = logging.getLogger(__name__)

# ⚙️ Discord-intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def setup_hook():
    logger.info("🔄 Laddar cogs...")

    # Ladda alla cogs från cogs-mappen
    for filename in os.listdir(COGS_DIR):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"✅ Laddade cogs.{filename[:-3]}")
            except Exception as e:
                logger.error(f"❌ Kunde inte ladda {filename}: {e}")

    # Synka slash commands
    try:
        await bot.tree.sync()
        logger.info("✅ Slash commands synkade!")
    except Exception as e:
        logger.error(f"❌ Slash sync misslyckades: {e}")

@bot.event
async def on_ready():
    logger.info("=" * 50)
    logger.info(f"🎲 {BOT_NAME} är online!")
    logger.info(f"📛 Namn: {bot.user.name}")
    logger.info(f"🆔 ID: {bot.user.id}")
    logger.info(f"🌐 Servrar: {len(bot.guilds)}")
    logger.info("=" * 50)

    await bot.change_presence(
        activity=discord.Game(name="D&D | /help")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har inte behörighet för detta kommando!")
    else:
        logger.warning(f"⚠️ Kommandofel: {error}")

@bot.command(name="sync")
@commands.is_owner()
async def sync_commands(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Slash commands synkade!")

def main():
    try:
        logger.info("🚀 Startar Puffen-RPG...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Ogiltig token! Kolla din miljövariabel")
    except Exception as e:
        logger.error(f"❌ Ett fel uppstod: {e}")

if __name__ == "__main__":
    main()
