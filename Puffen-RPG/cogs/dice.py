# ============================================
# FILE: cogs/dice.py
# ============================================
import discord
from discord.ext import commands
from discord import app_commands
import random

class DiceCog(commands.Cog):
    """Cog för alla tärningsrelaterade kommandon."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Slå tärningar (t.ex. 1d20, 2d6+3, 1d20adv)")
    async def roll(self, interaction: discord.Interaction, dice: str):
        """Slår tärningar med D&D notation."""
        try:
            dice = dice.lower().replace(" ", "")
            advantage = "adv" in dice
            disadvantage = "dis" in dice
            dice = dice.replace("adv", "").replace("dis", "")

            # Parse modifier
            modifier = 0
            if '+' in dice:
                dice, mod = dice.split('+')
                modifier = int(mod)
            elif '-' in dice and dice.count('-') == 1:
                dice, mod = dice.split('-')
                modifier = -int(mod)

            # Parse dice notation
            num_dice, die_size = dice.split('d')
            num_dice = int(num_dice) if num_dice else 1
            die_size = int(die_size)

            # Roll dice
            if advantage or disadvantage:
                rolls = [random.randint(1, die_size), random.randint(1, die_size)]
                result = max(rolls) if advantage else min(rolls)
                total = result + modifier
                adv_text = "**[Advantage]**" if advantage else "**[Disadvantage]**"
                embed = discord.Embed(
                    title=f"🎲 Tärningsslag {adv_text}",
                    description=f"**{dice}{'+'if modifier>=0 else ''}{modifier if modifier!=0 else ''}**",
                    color=discord.Color.green() if advantage else discord.Color.orange()
                )
                embed.add_field(name="Slag", value=f"{rolls[0]}, {rolls[1]} → **{result}**", inline=False)
                if modifier != 0:
                    embed.add_field(name="Modifier", value=f"{'+' if modifier>0 else ''}{modifier}", inline=True)
                embed.add_field(name="Totalt", value=f"**{total}**", inline=True)
            else:
                rolls = [random.randint(1, die_size) for _ in range(num_dice)]
                total = sum(rolls) + modifier

                embed = discord.Embed(
                    title="🎲 Tärningsslag",
                    description=f"**{num_dice}d{die_size}{'+'if modifier>=0 else ''}{modifier if modifier!=0 else ''}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Slag", value=f"{', '.join(map(str, rolls))} = {sum(rolls)}", inline=False)
                if modifier != 0:
                    embed.add_field(name="Modifier", value=f"{'+' if modifier>0 else ''}{modifier}", inline=True)
                embed.add_field(name="Totalt", value=f"**{total}**", inline=True)

            # Critical hit/fail för d20
            if die_size == 20 and num_dice == 1:
                if max(rolls) == 20:
                    embed.set_footer(text="🌟 CRITICAL HIT! 🌟")
                elif max(rolls) == 1:
                    embed.set_footer(text="💀 CRITICAL FAIL! 💀")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ogiltigt format! Använd t.ex: `1d20`, `2d6+3`, `1d20adv`, `1d20dis`",
                ephemeral=True
            )

    @app_commands.command(name="stats", description="Slå stats för en ny karaktär (4d6 drop lowest)")
    async def roll_stats(self, interaction: discord.Interaction):
        """Slår stats för en ny karaktär."""
        stats = []
        rolls_detail = []

        for i in range(6):
            rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
            stat_value = sum(rolls[:3])  # Ta de 3 högsta
            stats.append(stat_value)
            rolls_detail.append(f"**{stat_value}** ({', '.join(map(str, rolls[:3]))} ~~{rolls[3]}~~)")

        embed = discord.Embed(
            title="🎲 Slå Karaktärsstats",
            description="4d6 drop lowest för varje stat",
            color=discord.Color.gold()
        )

        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for name, detail in zip(stat_names, rolls_detail):
            embed.add_field(name=name, value=detail, inline=True)

        total = sum(stats)
        embed.set_footer(text=f"Totalt: {total} | Genomsnitt: {total/6:.1f}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))