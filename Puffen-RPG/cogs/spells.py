import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from config import DATA_FILE
import json
import os

class SpellsCog(commands.Cog):
    """Cog för spell tracking och hantering."""

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

    @app_commands.command(name="addspell", description="Lägg till en spell till din spellbook")
    async def add_spell(
        self,
        interaction: discord.Interaction,
        name: str,
        level: int,
        damage: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Lägger till en spell till karaktärens spellbook."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        if character.get('spells') is None:
            await interaction.response.send_message(
                f"❌ Din karaktär (**{character['class']}**) är inte en spellcaster!",
                ephemeral=True
            )
            return

        if level < 0 or level > 9:
            await interaction.response.send_message(
                "❌ Spell level måste vara mellan 0 (cantrip) och 9!",
                ephemeral=True
            )
            return

        spell = {
            "name": name,
            "level": level,
            "damage": damage,
            "description": description
        }

        character['spells'].append(spell)
        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        spell_type = "Cantrip" if level == 0 else f"Level {level} Spell"
        await interaction.response.send_message(
            f"✅ **{name}** ({spell_type}) tillagd till din spellbook!"
        )

    @app_commands.command(name="spellbook", description="Visa dina spells")
    async def show_spellbook(self, interaction: discord.Interaction, target: Optional[discord.Member] = None):
        """Visar karaktärens spellbook."""
        target_user = target or interaction.user
        character = self.get_character(str(target_user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {'Du har' if not target else f'{target_user.display_name} har'} ingen karaktär!",
                ephemeral=True
            )
            return

        if character.get('spells') is None:
            await interaction.response.send_message(
                f"❌ {character['name']} (**{character['class']}**) är inte en spellcaster!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📖 {character['name']}'s Spellbook",
            description=f"**{character['class']}** | Level {character['level']}",
            color=discord.Color.purple()
        )

        if not character['spells']:
            embed.description += "\n\n*Spellbook är tom! Använd `/addspell` för att lägga till spells.*"
        else:
            # Gruppera spells efter level
            for spell_level in range(10):  # 0-9
                spells_at_level = [s for s in character['spells'] if s['level'] == spell_level]
                if spells_at_level:
                    level_name = "Cantrips" if spell_level == 0 else f"Level {spell_level}"
                    spells_text = ""
                    for spell in spells_at_level:
                        spells_text += f"• **{spell['name']}**"
                        if spell.get('damage'):
                            spells_text += f" ({spell['damage']})"
                        if spell.get('description'):
                            spells_text += f"\n  *{spell['description']}*"
                        spells_text += "\n"
                    embed.add_field(name=f"✨ {level_name}", value=spells_text, inline=False)

        # Visa spell slots
        if character.get('spell_slots'):
            slots_text = ""
            for i, (total, used) in enumerate(zip(character['spell_slots'], character['spell_slots_used']), 1):
                if total > 0:
                    remaining = total - used
                    slots_text += f"**Lvl {i}**: {'○' * remaining}{'●' * used} ({remaining}/{total})\n"
            if slots_text:
                embed.add_field(name="🔮 Spell Slots", value=slots_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cast", description="Casta en spell och använd en spell slot")
    async def cast_spell(
        self,
        interaction: discord.Interaction,
        spell_name: str,
        spell_level: Optional[int] = None
    ):
        """Castar en spell och använder en spell slot."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        if character.get('spells') is None:
            await interaction.response.send_message(
                f"❌ Din karaktär (**{character['class']}**) är inte en spellcaster!",
                ephemeral=True
            )
            return

        # Hitta spellen
        spell = None
        for s in character['spells']:
            if s['name'].lower() == spell_name.lower():
                spell = s
                break

        if not spell:
            await interaction.response.send_message(
                f"❌ Kunde inte hitta spellen **{spell_name}** i din spellbook!",
                ephemeral=True
            )
            return

        # Om det är en cantrip, ingen spell slot behövs
        if spell['level'] == 0:
            embed = discord.Embed(
                title=f"✨ {character['name']} castar {spell['name']}!",
                description="**Cantrip** - ingen spell slot används",
                color=discord.Color.blue()
            )
            if spell.get('damage'):
                embed.add_field(name="💥 Damage", value=spell['damage'], inline=True)
            if spell.get('description'):
                embed.add_field(name="📝 Description", value=spell['description'], inline=False)
            await interaction.response.send_message(embed=embed)
            return

        # Bestäm vilken level att casta på
        cast_level = spell_level if spell_level is not None else spell['level']

        if cast_level < spell['level']:
            await interaction.response.send_message(
                f"❌ Kan inte casta en level {spell['level']} spell med en level {cast_level} spell slot!",
                ephemeral=True
            )
            return

        if cast_level < 1 or cast_level > 9:
            await interaction.response.send_message(
                "❌ Spell level måste vara mellan 1 och 9!",
                ephemeral=True
            )
            return

        # Kolla om det finns spell slots kvar
        slot_index = cast_level - 1
        if character['spell_slots'][slot_index] <= character['spell_slots_used'][slot_index]:
            await interaction.response.send_message(
                f"❌ Inga level {cast_level} spell slots kvar!",
                ephemeral=True
            )
            return

        # Använd spell slot
        character['spell_slots_used'][slot_index] += 1
        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        # Skapa embed
        embed = discord.Embed(
            title=f"✨ {character['name']} castar {spell['name']}!",
            description=f"**Level {cast_level} Spell Slot** används",
            color=discord.Color.purple()
        )

        if spell.get('damage'):
            embed.add_field(name="💥 Damage", value=spell['damage'], inline=True)
        if spell.get('description'):
            embed.add_field(name="📝 Description", value=spell['description'], inline=False)

        # Visa återstående slots
        remaining = character['spell_slots'][slot_index] - character['spell_slots_used'][slot_index]
        embed.set_footer(text=f"Level {cast_level} slots: {remaining}/{character['spell_slots'][slot_index]} kvar")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="longrest", description="Ta en long rest och återställ HP och spell slots")
    async def long_rest(self, interaction: discord.Interaction):
        """Tar en long rest och återställer HP och spell slots."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        # Återställ HP
        old_hp = character['hp']
        character['hp'] = character['max_hp']

        # Ta bort temp HP
        character['temp_hp'] = 0

        # Återställ spell slots
        if character.get('spell_slots_used'):
            character['spell_slots_used'] = [0] * 9

        # Ta bort vissa conditions (inte alla)
        if character.get('conditions'):
            # Behåll bara permanenta conditions
            permanent_conditions = []
            character['conditions'] = permanent_conditions

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title=f"😴 {character['name']} tar en Long Rest",
            description="8 timmars vila...",
            color=discord.Color.green()
        )

        embed.add_field(name="❤️ HP Återställt", value=f"{old_hp} → {character['hp']}/{character['max_hp']}", inline=False)

        if character.get('spell_slots'):
            embed.add_field(name="✨ Spell Slots", value="Alla spell slots återställda!", inline=False)

        embed.add_field(name="🎭 Conditions", value="De flesta conditions borttagna", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shortrest", description="Ta en short rest och slå hit dice för healing")
    async def short_rest(self, interaction: discord.Interaction, hit_dice: int = 1):
        """Tar en short rest och använder hit dice för healing."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        if hit_dice < 1:
            await interaction.response.send_message(
                "❌ Du måste använda minst 1 hit dice!",
                ephemeral=True
            )
            return

        # Slå hit dice (d6 för simplicitet, kan anpassas per class)
        con_mod = (character['stats']['constitution'] - 10) // 2
        healing = 0
        rolls = []

        for _ in range(hit_dice):
            roll = random.randint(1, 6)
            rolls.append(roll)
            healing += roll + con_mod

        old_hp = character['hp']
        character['hp'] = min(character['hp'] + healing, character['max_hp'])
        actual_healing = character['hp'] - old_hp

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title=f"☕ {character['name']} tar en Short Rest",
            description=f"Använder {hit_dice} hit dice",
            color=discord.Color.blue()
        )

        rolls_text = " + ".join([str(r) for r in rolls])
        embed.add_field(
            name="🎲 Hit Dice Rolls",
            value=f"{rolls_text} + {con_mod * hit_dice} (CON) = {healing} healing",
            inline=False
        )
        embed.add_field(
            name="❤️ HP",
            value=f"{old_hp} → {character['hp']}/{character['max_hp']} (+{actual_healing})",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SpellsCog(bot))