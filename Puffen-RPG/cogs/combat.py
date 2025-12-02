# ============================================
# FILE: cogs/combat.py
# ============================================
import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from config import DATA_FILE
import json
import os

class CombatCog(commands.Cog):
    """Cog för strid och combat-relaterade kommandon."""

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

    @app_commands.command(name="initiative", description="Slå initiative för strid")
    async def initiative(self, interaction: discord.Interaction):
        """Slår initiative (d20 + DEX modifier)."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        dex_mod = (character['stats']['dexterity'] - 10) // 2
        roll = random.randint(1, 20)
        total = roll + dex_mod

        embed = discord.Embed(
            title=f"🎲 {character['name']} - Initiative",
            description=f"1d20 ({roll}) + {dex_mod} = **{total}**",
            color=discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="attack", description="Gör en attack med ditt vapen")
    async def attack(self, interaction: discord.Interaction, target: Optional[str] = "target"):
        """Gör en attack roll och damage roll."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        # Hitta vapen
        weapons = [i for i in character['inventory'] if i['type'] == 'Weapon' and i.get('damage')]
        if not weapons:
            await interaction.response.send_message(
                "❌ Du har inget vapen med damage! Lägg till ett med `/additem`",
                ephemeral=True
            )
            return

        weapon = weapons[0]

        # Attack roll
        str_mod = (character['stats']['strength'] - 10) // 2
        dex_mod = (character['stats']['dexterity'] - 10) // 2
        attack_mod = max(str_mod, dex_mod) + character['proficiency']

        attack_roll = random.randint(1, 20)
        attack_total = attack_roll + attack_mod

        embed = discord.Embed(
            title=f"⚔️ {character['name']} attackerar {target}!",
            description=f"Vapen: **{weapon['name']}**",
            color=discord.Color.red()
        )

        embed.add_field(
            name="🎯 Attack Roll",
            value=f"1d20 ({attack_roll}) + {attack_mod} = **{attack_total}**",
            inline=False
        )

        # Damage roll
        if attack_roll != 1:
            damage_dice = weapon['damage']
            num_dice, die_size = damage_dice.split('d')
            num_dice = int(num_dice)
            die_size = int(die_size)

            if attack_roll == 20:
                num_dice *= 2
                embed.add_field(name="🌟 CRITICAL HIT!", value="Dubbel damage!", inline=False)

            damage_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            damage_mod = max(str_mod, dex_mod)
            damage_total = sum(damage_rolls) + damage_mod

            embed.add_field(
                name="💥 Damage",
                value=f"{damage_dice}: {', '.join(map(str, damage_rolls))} + {damage_mod} = **{damage_total}**",
                inline=False
            )
        else:
            embed.add_field(name="💀 CRITICAL FAIL!", value="Attacken missar helt!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="heal", description="Heala dig själv eller en annan spelare")
    async def heal(
        self,
        interaction: discord.Interaction,
        amount: int,
        target: Optional[discord.Member] = None
    ):
        """Healar en karaktär."""
        target_user = target or interaction.user
        character = self.get_character(str(target_user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target_user.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        old_hp = character['hp']
        character['hp'] = min(character['hp'] + amount, character['max_hp'])
        actual_heal = character['hp'] - old_hp

        self.save_character(str(target_user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title=f"💚 {character['name']} healas!",
            description=f"+{actual_heal} HP",
            color=discord.Color.green()
        )
        embed.add_field(name="HP", value=f"{old_hp} → {character['hp']}/{character['max_hp']}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CombatCog(bot))