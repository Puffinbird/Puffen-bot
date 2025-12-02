import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal, Optional
from config import DATA_FILE
import json
import os

class GMCog(commands.Cog):
    """Cog för GM (Game Master) kommandon."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = DATA_FILE
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Initiera npcs och monsters om de inte finns
                if 'npcs' not in data:
                    data['npcs'] = {}
                if 'monsters' not in data:
                    data['monsters'] = {}
                return data
        return {"characters": {}, "npcs": {}, "monsters": {}}

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

    @app_commands.command(name="damage", description="[GM] Ge skada till en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def damage(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        amount: int
    ):
        """[GM] Ge skada till en spelare."""
        character = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        old_hp = character['hp']
        old_temp = character.get('temp_hp', 0)

        # Damage tar först temp HP
        if old_temp > 0:
            if amount <= old_temp:
                character['temp_hp'] -= amount
                damage_to_hp = 0
            else:
                damage_to_hp = amount - old_temp
                character['temp_hp'] = 0
        else:
            damage_to_hp = amount

        character['hp'] = max(0, character['hp'] - damage_to_hp)

        self.save_character(str(target.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title=f"💔 {character['name']} tar skada!",
            description=f"-{amount} damage",
            color=discord.Color.red()
        )

        if old_temp > 0:
            embed.add_field(
                name="🛡️ Temp HP",
                value=f"{old_temp} → {character['temp_hp']}",
                inline=True
            )

        embed.add_field(
            name="❤️ HP",
            value=f"{old_hp} → {character['hp']}/{character['max_hp']}",
            inline=True
        )

        if character['hp'] == 0:
            embed.set_footer(text="☠️ Karaktären är nere!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="giveitem", description="[GM] Ge ett item till en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def give_item(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        item_name: str,
        item_type: Literal["Weapon", "Armor", "Consumable", "Misc"] = "Misc",
        damage: str = None,
        ac_bonus: int = None
    ):
        """[GM] Ger ett item till en spelare."""
        character = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        item = {
            "name": item_name,
            "type": item_type,
            "damage": damage,
            "ac_bonus": ac_bonus
        }
        character['inventory'].append(item)
        self.save_character(str(target.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ **{item_name}** har getts till {character['name']}!"
        )

    @app_commands.command(name="givexp", description="[GM] Ge XP till en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def give_xp(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        xp: int
    ):
        """[GM] Ger XP till en spelare."""
        character = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        character['xp'] += xp
        self.save_character(str(target.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ **{character['name']}** fick {xp} XP! (Totalt: {character['xp']} XP)"
        )

    @app_commands.command(name="givegold", description="[GM] Ge guld till en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def give_gold(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        gold: int
    ):
        """[GM] Ger guld till en spelare."""
        character = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        character['gold'] += gold
        self.save_character(str(target.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ **{character['name']}** fick {gold} gold! (Totalt: {character['gold']} gp)"
        )

    @app_commands.command(name="party", description="Visa alla karaktärer i gruppen")
    async def show_party(self, interaction: discord.Interaction):
        """Visar alla karaktärer i servern."""
        guild_chars = {k: v for k, v in self.data["characters"].items()
                      if k.startswith(f"{interaction.guild.id}_")}

        if not guild_chars:
            await interaction.response.send_message("❌ Inga karaktärer finns i denna server!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"👥 Party - {interaction.guild.name}",
            description=f"Totalt {len(guild_chars)} karaktärer",
            color=discord.Color.blue()
        )

        for key, char in guild_chars.items():
            user_id = key.split('_')[1]
            member = interaction.guild.get_member(int(user_id))
            hp_bar = "█" * int((char['hp'] / char['max_hp']) * 5) + "░" * (5 - int((char['hp'] / char['max_hp']) * 5))

            char_info = f"**{char['class']} {char['level']}** | HP: {hp_bar} {char['hp']}/{char['max_hp']}\n"
            char_info += f"AC: {char['ac']} | Gold: {char['gold']}gp"

            if char.get('conditions'):
                char_info += f"\n🎭 {', '.join(char['conditions'])}"

            embed.add_field(
                name=f"⚔️ {char['name']} ({member.display_name if member else 'Unknown'})",
                value=char_info,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sethp", description="[GM] Sätt HP för en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_hp(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        hp: int
    ):
        """[GM] Sätter HP för en spelare."""
        character = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {target.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        character['hp'] = max(0, min(hp, character['max_hp']))
        self.save_character(str(target.id), str(interaction.guild.id), character)

        await interaction.response.send_message(
            f"✅ **{character['name']}**'s HP är nu {character['hp']}/{character['max_hp']}"
        )

    @app_commands.command(name="createnpc", description="[GM] Skapa en NPC")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_npc(
        self,
        interaction: discord.Interaction,
        name: str,
        hp: int = 10,
        ac: int = 10,
        description: Optional[str] = None
    ):
        """[GM] Skapar en NPC."""
        key = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        npc = {
            "name": name,
            "hp": hp,
            "max_hp": hp,
            "ac": ac,
            "description": description,
            "guild_id": str(interaction.guild.id)
        }

        self.data["npcs"][key] = npc
        self.save_data()

        embed = discord.Embed(
            title=f"👤 NPC Skapad: {name}",
            description=description or "*Ingen beskrivning*",
            color=discord.Color.green()
        )
        embed.add_field(name="❤️ HP", value=f"{hp}", inline=True)
        embed.add_field(name="🛡️ AC", value=f"{ac}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="createmonster", description="[GM] Skapa ett monster")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_monster(
        self,
        interaction: discord.Interaction,
        name: str,
        hp: int,
        ac: int,
        attack_bonus: int = 5,
        damage: str = "1d8+3",
        description: Optional[str] = None
    ):
        """[GM] Skapar ett monster."""
        key = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        monster = {
            "name": name,
            "hp": hp,
            "max_hp": hp,
            "ac": ac,
            "attack_bonus": attack_bonus,
            "damage": damage,
            "description": description,
            "guild_id": str(interaction.guild.id)
        }

        self.data["monsters"][key] = monster
        self.save_data()

        embed = discord.Embed(
            title=f"👹 Monster Skapat: {name}",
            description=description or "*Ingen beskrivning*",
            color=discord.Color.red()
        )
        embed.add_field(name="❤️ HP", value=f"{hp}", inline=True)
        embed.add_field(name="🛡️ AC", value=f"{ac}", inline=True)
        embed.add_field(name="⚔️ Attack", value=f"+{attack_bonus} ({damage})", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="npcs", description="[GM] Visa alla NPCs")
    async def show_npcs(self, interaction: discord.Interaction):
        """Visar alla NPCs i servern."""
        guild_npcs = {k: v for k, v in self.data["npcs"].items()
                     if v.get('guild_id') == str(interaction.guild.id)}

        if not guild_npcs:
            await interaction.response.send_message("❌ Inga NPCs finns i denna server!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"👥 NPCs - {interaction.guild.name}",
            description=f"Totalt {len(guild_npcs)} NPCs",
            color=discord.Color.green()
        )

        for key, npc in guild_npcs.items():
            hp_bar = "█" * int((npc['hp'] / npc['max_hp']) * 5) + "░" * (5 - int((npc['hp'] / npc['max_hp']) * 5))
            npc_info = f"HP: {hp_bar} {npc['hp']}/{npc['max_hp']} | AC: {npc['ac']}"
            if npc.get('description'):
                npc_info += f"\n*{npc['description']}*"

            embed.add_field(
                name=f"👤 {npc['name']}",
                value=npc_info,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="monsters", description="[GM] Visa alla monsters")
    async def show_monsters(self, interaction: discord.Interaction):
        """Visar alla monsters i servern."""
        guild_monsters = {k: v for k, v in self.data["monsters"].items()
                         if v.get('guild_id') == str(interaction.guild.id)}

        if not guild_monsters:
            await interaction.response.send_message("❌ Inga monsters finns i denna server!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"👹 Monsters - {interaction.guild.name}",
            description=f"Totalt {len(guild_monsters)} monsters",
            color=discord.Color.red()
        )

        for key, monster in guild_monsters.items():
            hp_bar = "█" * int((monster['hp'] / monster['max_hp']) * 5) + "░" * (5 - int((monster['hp'] / monster['max_hp']) * 5))
            monster_info = f"HP: {hp_bar} {monster['hp']}/{monster['max_hp']}\n"
            monster_info += f"AC: {monster['ac']} | Attack: +{monster['attack_bonus']} ({monster['damage']})"
            if monster.get('description'):
                monster_info += f"\n*{monster['description']}*"

            embed.add_field(
                name=f"👹 {monster['name']}",
                value=monster_info,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="damagenpc", description="[GM] Ge skada till en NPC/Monster")
    @app_commands.checks.has_permissions(administrator=True)
    async def damage_npc(
        self,
        interaction: discord.Interaction,
        name: str,
        amount: int,
        is_monster: bool = False
    ):
        """[GM] Ger skada till en NPC eller monster."""
        key = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        entity_dict = self.data["monsters"] if is_monster else self.data["npcs"]
        entity_type = "Monster" if is_monster else "NPC"

        if key not in entity_dict:
            await interaction.response.send_message(
                f"❌ Kunde inte hitta {entity_type}: **{name}**",
                ephemeral=True
            )
            return

        entity = entity_dict[key]
        old_hp = entity['hp']
        entity['hp'] = max(0, entity['hp'] - amount)
        self.save_data()

        embed = discord.Embed(
            title=f"💔 {entity['name']} tar skada!",
            description=f"-{amount} damage",
            color=discord.Color.red()
        )
        embed.add_field(name="HP", value=f"{old_hp} → {entity['hp']}/{entity['max_hp']}")

        if entity['hp'] == 0:
            embed.set_footer(text=f"☠️ {entity['name']} är besegrad!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletenpc", description="[GM] Ta bort en NPC")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_npc(self, interaction: discord.Interaction, name: str):
        """[GM] Tar bort en NPC."""
        key = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        if key not in self.data["npcs"]:
            await interaction.response.send_message(
                f"❌ Kunde inte hitta NPC: **{name}**",
                ephemeral=True
            )
            return

        del self.data["npcs"][key]
        self.save_data()

        await interaction.response.send_message(f"✅ NPC **{name}** har tagits bort!")

    @app_commands.command(name="deletemonster", description="[GM] Ta bort ett monster")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_monster(self, interaction: discord.Interaction, name: str):
        """[GM] Tar bort ett monster."""
        key = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        if key not in self.data["monsters"]:
            await interaction.response.send_message(
                f"❌ Kunde inte hitta monster: **{name}**",
                ephemeral=True
            )
            return

        del self.data["monsters"][key]
        self.save_data()

        await interaction.response.send_message(f"✅ Monster **{name}** har tagits bort!")

async def setup(bot):
    await bot.add_cog(GMCog(bot))