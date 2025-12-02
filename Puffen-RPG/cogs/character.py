# ============================================
# FILE: cogs/character.py
# ============================================
import discord
from discord.ext import commands
from discord import app_commands
from config import DATA_FILE
import json
import os

class CharacterCog(commands.Cog):
    """Cog för karaktärshantering."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = DATA_FILE
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"characters": {}}

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_character(self, user_id: str, guild_id: str):
        key = f"{guild_id}_{user_id}"
        return self.data["characters"].get(key)

    def save_character(self, user_id: str, guild_id: str, character: dict):
        key = f"{guild_id}_{user_id}"
        self.data["characters"][key] = character
        self.save_data()

    # 🧑 Skapa karaktär
    @app_commands.command(name="createchar", description="Skapa en ny karaktär")
    async def create_character(self, interaction: discord.Interaction, name: str, hp: int, strength: int, dexterity: int):
        key = f"{interaction.guild.id}_{interaction.user.id}"

        if key in self.data["characters"]:
            await interaction.response.send_message("❌ Du har redan en karaktär!", ephemeral=True)
            return

        character = {
            "name": name,
            "hp": hp,
            "max_hp": hp,
            "stats": {
                "strength": strength,
                "dexterity": dexterity
            },
            "proficiency": 2,
            "inventory": []
        }

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)
        await interaction.response.send_message(f"✅ Karaktär **{name}** skapad med {hp} HP!")

    # 📜 Visa karaktärsblad
    @app_commands.command(name="sheet", description="Visa din karaktärsblad")
    async def show_sheet(self, interaction: discord.Interaction):
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📜 {character['name']}s Karaktärsblad",
            color=discord.Color.blue()
        )
        embed.add_field(name="HP", value=f"{character['hp']}/{character['max_hp']}", inline=False)
        embed.add_field(name="Strength", value=str(character['stats']['strength']), inline=True)
        embed.add_field(name="Dexterity", value=str(character['stats']['dexterity']), inline=True)
        embed.add_field(name="Proficiency", value=str(character['proficiency']), inline=True)

        await interaction.response.send_message(embed=embed)

    # ✏️ Uppdatera karaktär
    @app_commands.command(name="updatechar", description="Uppdatera din karaktärs stats")
    async def update_character(self, interaction: discord.Interaction, hp: int = None, strength: int = None, dexterity: int = None):
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        if hp is not None:
            character['hp'] = hp
            character['max_hp'] = max(character['max_hp'], hp)
        if strength is not None:
            character['stats']['strength'] = strength
        if dexterity is not None:
            character['stats']['dexterity'] = dexterity

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)
        await interaction.response.send_message(f"✅ Karaktär **{character['name']}** uppdaterad!")

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
