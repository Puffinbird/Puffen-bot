# ============================================
# FILE: cogs/character.py
# ============================================
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from config import DATA_FILE
import json
import os

# Fördefinierade statspaket (alla summerar till 30 poäng)
PRESETS = {
    "Balanced": {"strength": 6, "speed": 6, "charisma": 6, "intelligence": 6, "health": 6},
    "Tank": {"strength": 8, "speed": 4, "charisma": 4, "intelligence": 4, "health": 10},
    "Speedster": {"strength": 4, "speed": 10, "charisma": 4, "intelligence": 6, "health": 6},
    "Face": {"strength": 4, "speed": 4, "charisma": 10, "intelligence": 6, "health": 6},
    "Mage": {"strength": 4, "speed": 4, "charisma": 6, "intelligence": 10, "health": 6}
}

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

    # 🧑 Skapa karaktär med preset
    @app_commands.command(name="createchar", description="Skapa en ny karaktär med färdiga stats")
    async def create_character(
        self,
        interaction: discord.Interaction,
        name: str,
        char_class: Literal["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Paladin", "Barbarian", "Bard", "Druid", "Warlock", "Monk", "Sorcerer"] = "Fighter",
        preset: Literal["Balanced", "Tank", "Speedster", "Face", "Mage"] = "Balanced"
    ):
        key = f"{interaction.guild.id}_{interaction.user.id}"

        if key in self.data["characters"]:
            await interaction.response.send_message("❌ Du har redan en karaktär! Använd `/deletechar` först.", ephemeral=True)
            return

        stats = PRESETS[preset]
        strength = stats["strength"]
        speed = stats["speed"]
        charisma = stats["charisma"]
        intelligence = stats["intelligence"]
        health = stats["health"]

        max_hp = health * 5
        ac = 10 + (speed // 2)

        character = {
            "name": name,
            "class": char_class,
            "level": 1,
            "xp": 0,
            "stats": stats,
            "hp": max_hp,
            "max_hp": max_hp,
            "temp_hp": 0,
            "ac": ac,
            "proficiency": 2,
            "inventory": [],
            "gold": 0,
            "conditions": [],
            "spells": None,
            "spell_slots": None,
            "spell_slots_used": None
        }

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title=f"⚔️ Karaktär Skapad: {name}",
            description=f"**{char_class}** | Level {1}\nHP: {max_hp} | AC: {ac}",
            color=discord.Color.gold()
        )

        stats_text = "\n".join([f"**{k.capitalize()}**: {v}" for k, v in stats.items()])
        embed.add_field(name=f"📊 Stats (Preset: {preset})", value=stats_text, inline=False)
        embed.add_field(name="💡 Tips", value="Varje Health poäng = 5 HP\nSpeed påverkar AC", inline=False)

        await interaction.response.send_message(embed=embed)

    # 📜 Visa karaktärsblad
    @app_commands.command(name="sheet", description="Visa din karaktärsblad")
    async def show_sheet(self, interaction: discord.Interaction, target: Optional[discord.Member] = None):
        target_user = target or interaction.user
        character = self.get_character(str(target_user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {'Du har' if not target else f'{target_user.display_name} har'} ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"⚔️ {character['name']}",
            description=f"**{character['class']}** | Level {character['level']} | XP: {character['xp']}",
            color=discord.Color.blue()
        )

        hp_percentage = character['hp'] / character['max_hp']
        hp_bar = "█" * int(hp_percentage * 10) + "░" * (10 - int(hp_percentage * 10))
        hp_text = f"{hp_bar}\n{character['hp']}/{character['max_hp']}"
        if character.get('temp_hp', 0) > 0:
            hp_text += f" (+{character['temp_hp']} temp)"
        embed.add_field(name="❤️ HP", value=hp_text, inline=False)

        stats_text = "\n".join([f"**{stat.capitalize()}**: {value}" for stat, value in character["stats"].items()])
        embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        combat_text = f"**AC**: {character['ac']}\n**Proficiency**: +{character['proficiency']}"
        embed.add_field(name="⚔️ Combat", value=combat_text, inline=True)

        if character.get('conditions'):
            conditions_text = ", ".join(character['conditions'])
            embed.add_field(name="🎭 Conditions", value=conditions_text, inline=False)

        if character['inventory']:
            inv_text = "\n".join([f"• {item['name']}" for item in character['inventory'][:3]])
            if len(character['inventory']) > 3:
                inv_text += f"\n... och {len(character['inventory']) - 3} till"
        else:
            inv_text = "*Tomt*"
        embed.add_field(name="🎒 Inventory", value=inv_text, inline=False)
        embed.add_field(name="💰 Gold", value=f"{character['gold']} gp", inline=True)

        await interaction.response.send_message(embed=embed)

    # ✏️ Uppdatera karaktär
    @app_commands.command(name="updatechar", description="Uppdatera din karaktärs stats")
    async def update_character(
        self,
        interaction: discord.Interaction,
        preset: Optional[Literal["Balanced", "Tank", "Speedster", "Face", "Mage"]] = None
    ):
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        if not preset:
            await interaction.response.send_message("❌ Du måste välja ett preset för att uppdatera!", ephemeral=True)
            return

        stats = PRESETS[preset]
        character['stats'] = stats
        character['max_hp'] = stats['health'] * 5
        character['hp'] = min(character['hp'], character['max_hp'])
        character['ac'] = 10 + (stats['speed'] // 2)

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ Karaktär **{character['name']}** uppdaterad till preset {preset}!\n"
            f"Max HP: {character['max_hp']} | AC: {character['ac']}"
        )

    # 🗑️ Ta bort karaktär
    @app_commands.command(name="deletechar", description="Ta bort din karaktär")
    async def delete_character(self, interaction: discord.Interaction):
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response
            key = f"{interaction.guild.id}_{interaction.user.id}"
            del self.data["characters"][key]
            self.save_data()

            await interaction.response.send_message(f"✅ **{character['name']}** har tagits bort!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
