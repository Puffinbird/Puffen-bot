import discord
from discord.ext import commands
import asyncio
import os

BOT_NAME = "Puffen-RPG"
TOKEN = os.getenv(f"{BOT_NAME.upper().replace('-', '_')}_TOKEN")
if not TOKEN:
    raise RuntimeError(f"❌ TOKEN för {BOT_NAME} saknas i miljön")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def setup_hook():
    """Laddar alla cogs när boten startar."""
    print("🔄 Laddar cogs...")

    # Ladda alla cogs från cogs mappen
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Laddade cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Kunde inte ladda {filename}: {e}")

    # Synka slash commands
    print("🔄 Synkar slash commands...")
    await bot.tree.sync()
    print("✅ Slash commands synkade!")

@bot.event
async def on_ready():
    """Körs när boten är redo."""
    print(f"\n{'='*50}")
    print(f"🎲 {BOT_NAME} är online!")
    print(f"📛 Namn: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Servrar: {len(bot.guilds)}")
    print(f"{'='*50}\n")

    # Sätt bot status
    await bot.change_presence(
        activity=discord.Game(name="D&D | /help")
    )

@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har inte behörighet för detta kommando!")
    else:
        print(f"Error: {error}")

@bot.command(name="sync")
@commands.is_owner()
async def sync_commands(ctx):
    """Synkar slash commands manuellt (endast bot owner)."""
    await bot.tree.sync()
    await ctx.send("✅ Slash commands synkade!")

def main():
    """Huvudfunktion för att starta boten."""
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Ogiltig token! Kolla din miljövariabel")
    except Exception as e:
        print(f"❌ Ett fel uppstod: {e}")

if __name__ == "__main__":
    main()