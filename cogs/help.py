# ==================== HELP.PY ====================
import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils_core import generate_help_embed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        help="Visa alla kommandon"
    )
    async def help_command(self, ctx):
        """Visa hjälp om alla kommandon"""
        commands_list = [cmd for cmd in self.bot.tree.get_commands()]
        is_admin = ctx.author.guild_permissions.administrator if ctx.guild else False

        embed = generate_help_embed(commands_list, is_admin)
        await ctx.send(embed=embed)

    @app_commands.command(
        name="help",
        description="Visa alla kommandon",
        extras={"cog": "Hjälp", "help_text": "Visar en lista över alla tillgängliga kommandon."}
    )
    async def slash_help(self, interaction: discord.Interaction):
        """Visa hjälp om alla kommandon"""
        commands_list = interaction.client.tree.get_commands()
        is_admin = interaction.user.guild_permissions.administrator if interaction.guild else False

        embed = generate_help_embed(commands_list, is_admin)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))