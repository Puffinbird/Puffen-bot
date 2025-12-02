import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from config import DATA_FILE
import json
import os
import random

class LootCog(commands.Cog):
    """Cog för loot tables och random loot generation."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = DATA_FILE
        self.data = self.load_data()

        # Loot tables
        self.loot_tables = {
            "Common": {
                "gold": (1, 10),
                "items": [
                    {"name": "Rope (50 ft)", "type": "Misc", "weight": 20},
                    {"name": "Torch (10)", "type": "Misc", "weight": 20},
                    {"name": "Rations (10 days)", "type": "Consumable", "weight": 20},
                    {"name": "Bedroll", "type": "Misc", "weight": 15},
                    {"name": "Dagger", "type": "Weapon", "damage": "1d4", "weight": 15},
                    {"name": "Healing Potion", "type": "Consumable", "effect": "2d4+2", "weight": 10},
                ]
            },
            "Uncommon": {
                "gold": (10, 50),
                "items": [
                    {"name": "Shortsword", "type": "Weapon", "damage": "1d6", "weight": 15},
                    {"name": "Longsword", "type": "Weapon", "damage": "1d8", "weight": 15},
                    {"name": "Leather Armor", "type": "Armor", "ac_bonus": 1, "weight": 15},
                    {"name": "Healing Potion", "type": "Consumable", "effect": "2d4+2", "weight": 20},
                    {"name": "Greater Healing Potion", "type": "Consumable", "effect": "4d4+4", "weight": 10},
                    {"name": "Crossbow", "type": "Weapon", "damage": "1d8", "weight": 10},
                    {"name": "Shield", "type": "Armor", "ac_bonus": 2, "weight": 10},
                    {"name": "Lockpicks", "type": "Misc", "weight": 5},
                ]
            },
            "Rare": {
                "gold": (50, 200),
                "items": [
                    {"name": "Greatsword", "type": "Weapon", "damage": "2d6", "weight": 15},
                    {"name": "Longbow", "type": "Weapon", "damage": "1d8", "weight": 15},
                    {"name": "Chainmail", "type": "Armor", "ac_bonus": 6, "weight": 15},
                    {"name": "Greater Healing Potion", "type": "Consumable", "effect": "4d4+4", "weight": 20},
                    {"name": "Potion of Strength", "type": "Consumable", "effect": "+2 STR", "weight": 10},
                    {"name": "Ring of Protection (+1 AC)", "type": "Misc", "weight": 10},
                    {"name": "Amulet of Health (+2 CON)", "type": "Misc", "weight": 10},
                    {"name": "Cloak of Elvenkind (Stealth advantage)", "type": "Misc", "weight": 5},
                ]
            },
            "Epic": {
                "gold": (200, 1000),
                "items": [
                    {"name": "Flaming Longsword (+1, 1d6 fire)", "type": "Weapon", "damage": "1d8+1d6", "weight": 15},
                    {"name": "Frost Greatsword (+1, 1d6 cold)", "type": "Weapon", "damage": "2d6+1d6", "weight": 15},
                    {"name": "Plate Armor +1", "type": "Armor", "ac_bonus": 9, "weight": 15},
                    {"name": "Ring of Spell Storing", "type": "Misc", "weight": 10},
                    {"name": "Boots of Speed (Double movement)", "type": "Misc", "weight": 10},
                    {"name": "Belt of Giant Strength (+4 STR)", "type": "Misc", "weight": 10},
                    {"name": "Superior Healing Potion", "type": "Consumable", "effect": "8d4+8", "weight": 15},
                    {"name": "Staff of Power", "type": "Weapon", "damage": "1d6", "weight": 10},
                ]
            },
            "Legendary": {
                "gold": (1000, 5000),
                "items": [
                    {"name": "Holy Avenger (+3 Longsword)", "type": "Weapon", "damage": "1d8+3", "weight": 20},
                    {"name": "Vorpal Sword (Crit on 19-20)", "type": "Weapon", "damage": "2d6", "weight": 20},
                    {"name": "Armor of Invulnerability", "type": "Armor", "ac_bonus": 10, "weight": 20},
                    {"name": "Ring of Three Wishes", "type": "Misc", "weight": 15},
                    {"name": "Deck of Many Things", "type": "Misc", "weight": 10},
                    {"name": "Tome of Clear Thought (+2 INT)", "type": "Misc", "weight": 10},
                    {"name": "Supreme Healing Potion", "type": "Consumable", "effect": "10d4+20", "weight": 5},
                ]
            }
        }

        # Monster loot tables
        self.monster_loot = {
            "Goblin": "Common",
            "Orc": "Common",
            "Bandit": "Common",
            "Wolf": "Common",
            "Zombie": "Common",
            "Skeleton": "Common",
            "Hobgoblin": "Uncommon",
            "Bugbear": "Uncommon",
            "Ogre": "Uncommon",
            "Troll": "Rare",
            "Young Dragon": "Rare",
            "Vampire": "Rare",
            "Lich": "Epic",
            "Adult Dragon": "Epic",
            "Ancient Dragon": "Legendary",
            "Demon Lord": "Legendary"
        }

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

    def generate_loot(self, rarity: str, num_items: int = 1):
        """Genererar random loot från en loot table."""
        if rarity not in self.loot_tables:
            return None, []

        table = self.loot_tables[rarity]

        # Generate gold
        gold = random.randint(table["gold"][0], table["gold"][1])

        # Generate items
        items = []
        for _ in range(num_items):
            # Weighted random selection
            total_weight = sum(item["weight"] for item in table["items"])
            rand = random.randint(1, total_weight)

            cumulative = 0
            for item_template in table["items"]:
                cumulative += item_template["weight"]
                if rand <= cumulative:
                    item = {
                        "name": item_template["name"],
                        "type": item_template["type"],
                        "damage": item_template.get("damage"),
                        "ac_bonus": item_template.get("ac_bonus"),
                        "effect": item_template.get("effect")
                    }
                    items.append(item)
                    break

        return gold, items

    @app_commands.command(name="loot", description="[GM] Generera random loot")
    @app_commands.checks.has_permissions(administrator=True)
    async def generate_loot_command(
        self,
        interaction: discord.Interaction,
        rarity: Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"],
        num_items: int = 1,
        target: Optional[discord.Member] = None
    ):
        """[GM] Genererar och ger loot till en spelare."""
        if num_items < 1 or num_items > 10:
            await interaction.response.send_message(
                "❌ Num items måste vara mellan 1 och 10!",
                ephemeral=True
            )
            return

        gold, items = self.generate_loot(rarity, num_items)

        if not gold and not items:
            await interaction.response.send_message(
                "❌ Kunde inte generera loot!",
                ephemeral=True
            )
            return

        # If target specified, give loot
        if target:
            character = self.get_character(str(target.id), str(interaction.guild.id))

            if not character:
                await interaction.response.send_message(
                    f"❌ {target.display_name} har ingen karaktär!",
                    ephemeral=True
                )
                return

            character["gold"] += gold
            character["inventory"].extend(items)
            self.save_character(str(target.id), str(interaction.guild.id), character)

        # Create embed
        rarity_colors = {
            "Common": discord.Color.light_gray(),
            "Uncommon": discord.Color.green(),
            "Rare": discord.Color.blue(),
            "Epic": discord.Color.purple(),
            "Legendary": discord.Color.gold()
        }

        embed = discord.Embed(
            title=f"🎁 {rarity} Loot Generated!",
            description=f"{'Given to ' + target.display_name if target else 'Preview'}",
            color=rarity_colors.get(rarity, discord.Color.blue())
        )

        embed.add_field(name="💰 Gold", value=f"{gold} gp", inline=False)

        if items:
            items_text = ""
            for item in items:
                items_text += f"• **{item['name']}**"
                if item.get('damage'):
                    items_text += f" ({item['damage']} damage)"
                elif item.get('ac_bonus'):
                    items_text += f" (+{item['ac_bonus']} AC)"
                elif item.get('effect'):
                    items_text += f" ({item['effect']})"
                items_text += "\n"
            embed.add_field(name="🎒 Items", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loottable", description="Visa en loot table")
    async def show_loot_table(
        self,
        interaction: discord.Interaction,
        rarity: Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    ):
        """Visar innehållet i en loot table."""
        if rarity not in self.loot_tables:
            await interaction.response.send_message(
                f"❌ Loot table **{rarity}** finns inte!",
                ephemeral=True
            )
            return

        table = self.loot_tables[rarity]

        rarity_colors = {
            "Common": discord.Color.light_gray(),
            "Uncommon": discord.Color.green(),
            "Rare": discord.Color.blue(),
            "Epic": discord.Color.purple(),
            "Legendary": discord.Color.gold()
        }

        embed = discord.Embed(
            title=f"📜 {rarity} Loot Table",
            description=f"Gold: {table['gold'][0]}-{table['gold'][1]} gp",
            color=rarity_colors.get(rarity, discord.Color.blue())
        )

        items_by_type = {}
        for item in table["items"]:
            item_type = item["type"]
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)

        for item_type, items in items_by_type.items():
            items_text = ""
            for item in items:
                items_text += f"• **{item['name']}**"
                if item.get('damage'):
                    items_text += f" ({item['damage']})"
                elif item.get('ac_bonus'):
                    items_text += f" (+{item['ac_bonus']} AC)"
                elif item.get('effect'):
                    items_text += f" ({item['effect']})"
                items_text += f" - {item['weight']}% chance\n"

            embed.add_field(name=f"⚔️ {item_type}", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="monsterloot", description="[GM] Generera loot från ett monster")
    @app_commands.checks.has_permissions(administrator=True)
    async def monster_loot(
        self,
        interaction: discord.Interaction,
        monster_type: str,
        target: Optional[discord.Member] = None
    ):
        """[GM] Genererar loot baserat på monster typ."""
        # Find monster in loot table (case insensitive)
        rarity = None
        actual_monster = None
        for monster, loot_rarity in self.monster_loot.items():
            if monster.lower() == monster_type.lower():
                rarity = loot_rarity
                actual_monster = monster
                break

        if not rarity:
            # Default to Common if not found
            rarity = "Common"
            actual_monster = monster_type

        gold, items = self.generate_loot(rarity, random.randint(1, 3))

        # If target specified, give loot
        if target:
            character = self.get_character(str(target.id), str(interaction.guild.id))

            if not character:
                await interaction.response.send_message(
                    f"❌ {target.display_name} har ingen karaktär!",
                    ephemeral=True
                )
                return

            character["gold"] += gold
            character["inventory"].extend(items)
            self.save_character(str(target.id), str(interaction.guild.id), character)

        # Create embed
        embed = discord.Embed(
            title=f"💀 {actual_monster} Loot!",
            description=f"**Rarity:** {rarity}\n{'Given to ' + target.display_name if target else 'Preview'}",
            color=discord.Color.dark_red()
        )

        embed.add_field(name="💰 Gold", value=f"{gold} gp", inline=False)

        if items:
            items_text = ""
            for item in items:
                items_text += f"• **{item['name']}**"
                if item.get('damage'):
                    items_text += f" ({item['damage']})"
                elif item.get('ac_bonus'):
                    items_text += f" (+{item['ac_bonus']} AC)"
                elif item.get('effect'):
                    items_text += f" ({item['effect']})"
                items_text += "\n"
            embed.add_field(name="🎒 Items", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="monsterloottable", description="Visa monster → loot rarity mapping")
    async def show_monster_loot_table(self, interaction: discord.Interaction):
        """Visar vilka monsters som ger vilken rarity loot."""

        embed = discord.Embed(
            title="💀 Monster Loot Table",
            description="Vilka monsters ger vilken rarity loot",
            color=discord.Color.dark_red()
        )

        # Group by rarity
        by_rarity = {}
        for monster, rarity in self.monster_loot.items():
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(monster)

        rarity_icons = {
            "Common": "⚪",
            "Uncommon": "🟢",
            "Rare": "🔵",
            "Epic": "🟣",
            "Legendary": "🟡"
        }

        for rarity in ["Common", "Uncommon", "Rare", "Epic", "Legendary"]:
            if rarity in by_rarity:
                monsters = ", ".join(by_rarity[rarity])
                embed.add_field(
                    name=f"{rarity_icons.get(rarity, '⚪')} {rarity}",
                    value=monsters,
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rollloot", description="[GM] Slumpmässig loot till alla spelare i party")
    @app_commands.checks.has_permissions(administrator=True)
    async def roll_loot_party(
        self,
        interaction: discord.Interaction,
        rarity: Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    ):
        """[GM] Ger random loot till alla spelare i party."""
        # Get all characters in guild
        guild_chars = {k: v for k, v in self.data["characters"].items()
                      if k.startswith(f"{interaction.guild.id}_")}

        if not guild_chars:
            await interaction.response.send_message(
                "❌ Inga karaktärer finns i denna server!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🎁 Party Loot Distribution - {rarity}",
            description=f"Rolling loot for {len(guild_chars)} characters...",
            color=discord.Color.gold()
        )

        total_gold = 0
        total_items = 0

        for key, character in guild_chars.items():
            user_id = key.split('_')[1]

            # Generate loot
            gold, items = self.generate_loot(rarity, random.randint(1, 2))

            # Give loot
            character["gold"] += gold
            character["inventory"].extend(items)

            # Save
            self.data["characters"][key] = character

            # Track totals
            total_gold += gold
            total_items += len(items)

            # Add to embed
            items_text = f"💰 {gold} gp"
            if items:
                items_text += f"\n🎒 {len(items)} items: " + ", ".join([i['name'] for i in items])

            embed.add_field(
                name=f"⚔️ {character['name']}",
                value=items_text,
                inline=False
            )

        self.save_data()

        embed.set_footer(text=f"Total: {total_gold} gp, {total_items} items distributed")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="treasure", description="[GM] Skapa en treasure chest med custom loot")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_treasure(
        self,
        interaction: discord.Interaction,
        name: str,
        gold: int,
        description: Optional[str] = None
    ):
        """[GM] Skapar en treasure chest som spelare kan öppna."""
        if "treasures" not in self.data:
            self.data["treasures"] = {}

        treasure_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        if treasure_id in self.data["treasures"]:
            await interaction.response.send_message(
                f"❌ Treasure **{name}** finns redan!",
                ephemeral=True
            )
            return

        treasure = {
            "name": name,
            "gold": gold,
            "items": [],
            "description": description or "A mysterious treasure chest",
            "opened_by": [],
            "guild_id": str(interaction.guild.id)
        }

        self.data["treasures"][treasure_id] = treasure
        self.save_data()

        embed = discord.Embed(
            title=f"💎 Treasure Created: {name}",
            description=description or "A mysterious treasure chest",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Gold", value=f"{gold} gp", inline=True)
        embed.set_footer(text="Use /addtreasureitem to add items | Players use /opentreasure")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addtreasureitem", description="[GM] Lägg till ett item i en treasure chest")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_treasure_item(
        self,
        interaction: discord.Interaction,
        treasure_name: str,
        item_name: str,
        item_type: Literal["Weapon", "Armor", "Consumable", "Misc"],
        damage: Optional[str] = None,
        ac_bonus: Optional[int] = None
    ):
        """[GM] Lägger till ett item i en treasure chest."""
        if "treasures" not in self.data:
            self.data["treasures"] = {}

        treasure_id = f"{interaction.guild.id}_{treasure_name.lower().replace(' ', '_')}"

        if treasure_id not in self.data["treasures"]:
            await interaction.response.send_message(
                f"❌ Treasure **{treasure_name}** finns inte!",
                ephemeral=True
            )
            return

        treasure = self.data["treasures"][treasure_id]

        item = {
            "name": item_name,
            "type": item_type,
            "damage": damage,
            "ac_bonus": ac_bonus
        }

        treasure["items"].append(item)
        self.save_data()

        await interaction.response.send_message(
            f"✅ **{item_name}** tillagt till treasure **{treasure['name']}**!"
        )

    @app_commands.command(name="opentreasure", description="Öppna en treasure chest")
    async def open_treasure(self, interaction: discord.Interaction, treasure_name: str):
        """Öppnar en treasure chest och får loot."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär!",
                ephemeral=True
            )
            return

        if "treasures" not in self.data:
            self.data["treasures"] = {}

        treasure_id = f"{interaction.guild.id}_{treasure_name.lower().replace(' ', '_')}"

        if treasure_id not in self.data["treasures"]:
            await interaction.response.send_message(
                f"❌ Treasure **{treasure_name}** finns inte!",
                ephemeral=True
            )
            return

        treasure = self.data["treasures"][treasure_id]

        if str(interaction.user.id) in treasure["opened_by"]:
            await interaction.response.send_message(
                f"❌ Du har redan öppnat **{treasure['name']}**!",
                ephemeral=True
            )
            return

        # Give loot
        character["gold"] += treasure["gold"]
        character["inventory"].extend(treasure["items"])
        treasure["opened_by"].append(str(interaction.user.id))

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)
        self.save_data()

        embed = discord.Embed(
            title=f"💎 {character['name']} öppnar {treasure['name']}!",
            description=treasure["description"],
            color=discord.Color.gold()
        )

        embed.add_field(name="💰 Gold", value=f"+{treasure['gold']} gp", inline=False)

        if treasure["items"]:
            items_text = "\n".join([f"• **{item['name']}**" for item in treasure["items"]])
            embed.add_field(name="🎒 Items", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LootCog(bot))