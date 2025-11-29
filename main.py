# ==================== MAIN.PY ====================
import discord, os, asyncio, logging
from logging.handlers import RotatingFileHandler
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from cogs.config import config  # <-- laddar din config

# Se till att log-mappen finns
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Grundläggande loggning till konsolen
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kommandologg (roterande)
command_logger = logging.getLogger("commands")
command_handler = RotatingFileHandler("logs/commands.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
command_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
command_logger.addHandler(command_handler)
command_logger.setLevel(logging.INFO)

# Errorlogg (roterande)
error_logger = logging.getLogger("errors")
error_handler = RotatingFileHandler("logs/errors.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.WARNING)

# Token och intents
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    logger.error("❌ TOKEN saknas i miljön!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    """Laddas när botten startar"""
    cogs_to_load = [
        "cogs.utils_core",
        "cogs.fun",
        "cogs.roles",
        "cogs.quotes",
        "cogs.admin",
        "cogs.help",
    ]

    for ext in cogs_to_load:
        try:
            await bot.load_extension(ext)
            logger.info(f"✓ Laddade {ext}")
        except Exception as e:
            logger.error(f"⚠️ Kunde inte ladda {ext}: {e}")

    # Synka slash-commands
    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"🧹 Synkade {len(synced)} kommandon för {guild.name} ({guild.id})")
        except Exception as e:
            logger.error(f"⚠️ Kunde inte synka kommandon för {guild.name}: {e}")

    if not bot.guilds:
        try:
            synced = await bot.tree.sync()
            logger.info(f"🌍 Global sync: {len(synced)} kommandon registrerade")
        except Exception as e:
            logger.error(f"⚠️ Global sync misslyckades: {e}")

@bot.event
async def on_ready():
    """Körs när botten är redo"""
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=config.status
    ))
    logger.info(f"✅ {config.name} är online – version {config.version}")
    logger.info(f"📊 Aktiv på {len(bot.guilds)} server(ar)")
    logger.info(f"🎭 Status satt till: {config.status}")

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    """Loggar när ett slash-kommando körs"""
    user = interaction.user
    guild = interaction.guild.name if interaction.guild else "DM"
    command_logger.info(f"{user} körde /{command.name} i {guild} ({interaction.guild_id})")

@bot.tree.error
async def on_slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Hanterar fel i slash-kommandon"""
    user = interaction.user
    guild = interaction.guild.name if interaction.guild else "DM"
    command = interaction.command.name if interaction.command else "okänt"
    error_logger.warning(f"❌ Fel i /{command} av {user} i {guild}: {type(error).__name__} – {error}")

    try:
        await interaction.response.send_message(
            "⚠️ Ett fel uppstod med kommandot. Det har loggats för felsökning.",
            ephemeral=True
        )
    except discord.InteractionResponded:
        await interaction.followup.send(
            "⚠️ Ett fel uppstod med kommandot. Det har loggats för felsökning.",
            ephemeral=True
        )

if __name__ == "__main__":
    try:
        logger.info("🚀 Startar Puffin Discord Bot...")
        logger.info(f"🤖 Namn: {config.name} | Version: {config.version}")
        asyncio.run(bot.start(TOKEN))
    except KeyboardInterrupt:
        logger.info("🛑 Botten stoppades manuellt.")
        try:
            asyncio.run(bot.close())
        except Exception as e:
            logger.error(f"Fel vid stängning: {e}")
    except Exception as e:
        logger.error(f"🛑 Botten kraschade: {e}")
        raise
