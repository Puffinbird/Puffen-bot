import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
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

    @app_commands.command(name="createchar", description="Skapa en ny karaktär")
    async def create_character(
        self,
        interaction: discord.Interaction,
        name: str,
        char_class: Literal["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Paladin", "Barbarian", "Bard", "Druid", "Warlock", "Monk", "Sorcerer"] = "Fighter",
        strength: int = 6,
        speed: int = 6,
        charisma: int = 6,
        intelligence: int = 6,
        health: int = 6
    ):
        """Skapar en ny karaktär med 5 stats (totalt 30 poäng)."""
        key = f"{interaction.guild.id}_{interaction.user.id}"

        if key in self.data["characters"]:
            await interaction.response.send_message("❌ Du har redan en karaktär! Använd `/deletechar` först.", ephemeral=True)
            return

        # Validera stats
        total_points = strength + speed + charisma + intelligence + health
        if total_points != 30:
            await interaction.response.send_message(
                f"❌ Du måste fördela exakt 30 poäng! Du har använt {total_points} poäng.\n"
                f"**Nuvarande fördelning:**\n"
                f"Strength: {strength}\n"
                f"Speed: {speed}\n"
                f"Charisma: {charisma}\n"
                f"Intelligence: {intelligence}\n"
                f"Health: {health}",
                ephemeral=True
            )
            return

        # Validera att varje stat är minst 1
        if any(stat < 1 for stat in [strength, speed, charisma, intelligence, health]):
            await interaction.response.send_message("❌ Varje stat måste vara minst 1!", ephemeral=True)
            return

        # Beräkna HP baserat på health
        max_hp = health * 5  # Varje health poäng = 5 HP

        # Beräkna AC baserat på speed
        ac = 10 + (speed // 2)  # Base 10 + speed bonus

        character = {
            "name": name,
            "class": char_class,
            "level": 1,
            "xp": 0,
            "stats": {
                "strength": strength,
                "speed": speed,
                "charisma": charisma,
                "intelligence": intelligence,
                "health": health
            },
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

        # Visa stats med modifiers
        stats_text = ""
        for stat, value in character["stats"].items():
            stats_text += f"**{stat.capitalize()}**: {value}\n"

        embed.add_field(name="📊 Stats (30 poäng fördelade)", value=stats_text, inline=False)
        embed.add_field(name="💡 Tips", value="Varje Health poäng = 5 HP\nSpeed påverkar AC", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sheet", description="Visa din karaktärsblad")
    async def show_sheet(self, interaction: discord.Interaction, target: Optional[discord.Member] = None):
        """Visar spelarens karaktärsblad."""
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

        # HP bar
        hp_percentage = character['hp'] / character['max_hp']
        hp_bar = "█" * int(hp_percentage * 10) + "░" * (10 - int(hp_percentage * 10))
        hp_text = f"{hp_bar}\n{character['hp']}/{character['max_hp']}"
        if character.get('temp_hp', 0) > 0:
            hp_text += f" (+{character['temp_hp']} temp)"
        embed.add_field(name="❤️ HP", value=hp_text, inline=False)

        # Stats
        stats_text = ""
        for stat, value in character["stats"].items():
            stats_text += f"**{stat.capitalize()}**: {value}\n"
        embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        # Combat stats
        combat_text = f"**AC**: {character['ac']}\n**Proficiency**: +{character['proficiency']}"
        embed.add_field(name="⚔️ Combat", value=combat_text, inline=True)

        # Conditions
        if character.get('conditions'):
            conditions_text = ", ".join(character['conditions'])
            embed.add_field(name="🎭 Conditions", value=conditions_text, inline=False)

        # Inventory preview
        if character['inventory']:
            inv_text = "\n".join([f"• {item['name']}" for item in character['inventory'][:3]])
            if len(character['inventory']) > 3:
                inv_text += f"\n... och {len(character['inventory']) - 3} till"
        else:
            inv_text = "*Tomt*"
        embed.add_field(name="🎒 Inventory", value=inv_text, inline=False)
        embed.add_field(name="💰 Gold", value=f"{character['gold']} gp", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="updatechar", description="Uppdatera din karaktärs stats")
    async def update_character(
        self,
        interaction: discord.Interaction,
        strength: Optional[int] = None,
        speed: Optional[int] = None,
        charisma: Optional[int] = None,
        intelligence: Optional[int] = None,
        health: Optional[int] = None
    ):
        """Uppdaterar karaktärens stats (måste fortfarande totalt 30 poäng)."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        # Om inga ändringar specificerades
        if all(stat is None for stat in [strength, speed, charisma, intelligence, health]):
            await interaction.response.send_message(
                "❌ Du måste ange minst en stat att uppdatera!",
                ephemeral=True
            )
            return

        # Använd nuvarande värden om inget nytt anges
        new_strength = strength if strength is not None else character['stats']['strength']
        new_speed = speed if speed is not None else character['stats']['speed']
        new_charisma = charisma if charisma is not None else character['stats']['charisma']
        new_intelligence = intelligence if intelligence is not None else character['stats']['intelligence']
        new_health = health if health is not None else character['stats']['health']

        # Validera total poäng
        total_points = new_strength + new_speed + new_charisma + new_intelligence + new_health
        if total_points != 30:
            await interaction.response.send_message(
                f"❌ Du måste ha totalt 30 poäng! Du har {total_points} poäng.\n"
                f"**Ny fördelning:**\n"
                f"Strength: {new_strength}\n"
                f"Speed: {new_speed}\n"
                f"Charisma: {new_charisma}\n"
                f"Intelligence: {new_intelligence}\n"
                f"Health: {new_health}",
                ephemeral=True
            )
            return

        # Validera att varje stat är minst 1
        if any(stat < 1 for stat in [new_strength, new_speed, new_charisma, new_intelligence, new_health]):
            await interaction.response.send_message("❌ Varje stat måste vara minst 1!", ephemeral=True)
            return

        # Uppdatera stats
        character['stats'] = {
            "strength": new_strength,
            "speed": new_speed,
            "charisma": new_charisma,
            "intelligence": new_intelligence,
            "health": new_health
        }

        # Uppdatera härledda värden
        character['max_hp'] = new_health * 5
        character['hp'] = min(character['hp'], character['max_hp'])  # Se till att HP inte överstiger max
        character['ac'] = 10 + (new_speed // 2)

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ Karaktär **{character['name']}** uppdaterad!\n"
            f"Max HP: {character['max_hp']} | AC: {character['ac']}"
        )

    @app_commands.command(name="additem", description="Lägg till ett item till din inventory")
    async def add_item(
        self,
        interaction: discord.Interaction,
        name: str,
        item_type: Literal["Weapon", "Armor", "Consumable", "Misc"] = "Misc",
        damage: Optional[str] = None,
        ac_bonus: Optional[int] = None
    ):
        """Lägger till ett item till spelarens inventory."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        item = {
            "name": name,
            "type": item_type,
            "damage": damage,
            "ac_bonus": ac_bonus
        }

        character['inventory'].append(item)
        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        await interaction.response.send_message(f"✅ **{name}** tillagt till din inventory!")

    @app_commands.command(name="inventory", description="Visa din inventory")
    async def show_inventory(self, interaction: discord.Interaction, target: Optional[discord.Member] = None):
        """Visar spelarens inventory."""
        target_user = target or interaction.user
        character = self.get_character(str(target_user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {'Du har' if not target else f'{target_user.display_name} har'} ingen karaktär!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🎒 {character['name']}'s Inventory",
            description=f"💰 {character['gold']} gold pieces",
            color=discord.Color.purple()
        )

        if not character['inventory']:
            embed.description += "\n\n*Inventory är tom!*"
        else:
            for item_type in ["Weapon", "Armor", "Consumable", "Misc"]:
                items = [i for i in character['inventory'] if i['type'] == item_type]
                if items:
                    items_text = ""
                    for item in items:
                        items_text += f"• **{item['name']}**"
                        if item.get('damage'):
                            items_text += f" ({item['damage']} damage)"
                        if item.get('ac_bonus'):
                            items_text += f" (+{item['ac_bonus']} AC)"
                        items_text += "\n"
                    embed.add_field(name=f"⚔️ {item_type}", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletechar", description="Ta bort din karaktär")
    async def delete_character(self, interaction: discord.Interaction):
        """Tar bort spelarens karaktär."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        key = f"{interaction.guild.id}_{interaction.user.id}"
        del self.data["characters"][key]
        self.save_data()

        await interaction.response.send_message(f"✅ **{character['name']}** har tagits bort!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
