# ==================== ADMIN.PY ====================
import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
    name="reload",
    description="Reloada en cog",
    extras={"cog": "Admin", "help_text": "Laddar om en specifik cog. Exempel: `/reload fun`"})
    @app_commands.default_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, extension: str):
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await self.bot.load_extension(f"cogs.{extension}")
            await interaction.response.send_message(f"✅ Cog `{extension}` reloadad!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Kunde inte reloada:\n```{e}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))