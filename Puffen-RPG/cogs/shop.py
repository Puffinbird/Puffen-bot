import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from config import DATA_FILE
import json
import os

class ShopCog(commands.Cog):
    """Cog för item shop och handel."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = DATA_FILE
        self.data = self.load_data()

        # Standard shop items
        self.shop_items = {
            # Weapons
            "Dagger": {"type": "Weapon", "price": 2, "damage": "1d4", "description": "En liten kniv"},
            "Shortsword": {"type": "Weapon", "price": 10, "damage": "1d6", "description": "Ett kort svärd"},
            "Longsword": {"type": "Weapon", "price": 15, "damage": "1d8", "description": "Ett långt svärd"},
            "Greatsword": {"type": "Weapon", "price": 50, "damage": "2d6", "description": "Ett massivt tvåhandssvärd"},
            "Battleaxe": {"type": "Weapon", "price": 10, "damage": "1d8", "description": "En stridsyxa"},
            "Mace": {"type": "Weapon", "price": 5, "damage": "1d6", "description": "En klubba"},
            "Spear": {"type": "Weapon", "price": 1, "damage": "1d6", "description": "Ett spjut"},
            "Crossbow": {"type": "Weapon", "price": 25, "damage": "1d8", "description": "En armborst"},
            "Longbow": {"type": "Weapon", "price": 50, "damage": "1d8", "description": "En långbåge"},

            # Armor
            "Leather Armor": {"type": "Armor", "price": 10, "ac_bonus": 1, "description": "Lätt läderrustning"},
            "Chainmail": {"type": "Armor", "price": 75, "ac_bonus": 6, "description": "Ringbrynja"},
            "Plate Armor": {"type": "Armor", "price": 1500, "ac_bonus": 8, "description": "Full platrustning"},
            "Shield": {"type": "Armor", "price": 10, "ac_bonus": 2, "description": "En träsköld"},

            # Consumables
            "Healing Potion": {"type": "Consumable", "price": 50, "effect": "2d4+2", "description": "Återställer 2d4+2 HP"},
            "Greater Healing Potion": {"type": "Consumable", "price": 150, "effect": "4d4+4", "description": "Återställer 4d4+4 HP"},
            "Potion of Strength": {"type": "Consumable", "price": 100, "effect": "+2 STR", "description": "Ger +2 STR i 1 timme"},
            "Antidote": {"type": "Consumable", "price": 50, "effect": "Remove Poison", "description": "Tar bort poisoned condition"},
            "Rations (10 days)": {"type": "Consumable", "price": 5, "description": "Mat för 10 dagar"},

            # Misc
            "Rope (50 ft)": {"type": "Misc", "price": 1, "description": "50 fot rep"},
            "Torch (10)": {"type": "Misc", "price": 1, "description": "10 facklor"},
            "Backpack": {"type": "Misc", "price": 2, "description": "En ryggsäck"},
            "Bedroll": {"type": "Misc", "price": 1, "description": "En sovsäck"},
            "Lockpicks": {"type": "Misc", "price": 25, "description": "Verktyg för att öppna lås"},
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

    @app_commands.command(name="shop", description="Visa shop med alla tillgängliga items")
    async def show_shop(self, interaction: discord.Interaction, category: Optional[Literal["Weapon", "Armor", "Consumable", "Misc"]] = None):
        """Visar alla items i shoppen."""

        embed = discord.Embed(
            title="🏪 The Adventurer's Shop",
            description="Använd `/buy <item namn>` för att köpa ett item",
            color=discord.Color.gold()
        )

        categories = [category] if category else ["Weapon", "Armor", "Consumable", "Misc"]

        for cat in categories:
            items_in_cat = {name: item for name, item in self.shop_items.items() if item["type"] == cat}

            if items_in_cat:
                items_text = ""
                for name, item in sorted(items_in_cat.items(), key=lambda x: x[1]["price"]):
                    items_text += f"**{name}** - {item['price']}gp"
                    if item.get('damage'):
                        items_text += f" ({item['damage']})"
                    elif item.get('ac_bonus'):
                        items_text += f" (+{item['ac_bonus']} AC)"
                    elif item.get('effect'):
                        items_text += f" ({item['effect']})"
                    items_text += f"\n*{item['description']}*\n\n"

                icon = {"Weapon": "⚔️", "Armor": "🛡️", "Consumable": "🧪", "Misc": "📦"}
                embed.add_field(name=f"{icon[cat]} {cat}", value=items_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Köp ett item från shoppen")
    async def buy_item(self, interaction: discord.Interaction, item_name: str, quantity: int = 1):
        """Köper ett item från shoppen."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        # Hitta item (case insensitive)
        item_data = None
        actual_name = None
        for name, data in self.shop_items.items():
            if name.lower() == item_name.lower():
                item_data = data
                actual_name = name
                break

        if not item_data:
            await interaction.response.send_message(
                f"❌ Kunde inte hitta item: **{item_name}**\nAnvänd `/shop` för att se alla items.",
                ephemeral=True
            )
            return

        if quantity < 1:
            await interaction.response.send_message("❌ Quantity måste vara minst 1!", ephemeral=True)
            return

        total_cost = item_data["price"] * quantity

        if character["gold"] < total_cost:
            await interaction.response.send_message(
                f"❌ Du har inte råd! **{actual_name}** kostar {total_cost}gp (x{quantity}), du har {character['gold']}gp.",
                ephemeral=True
            )
            return

        # Köp item
        character["gold"] -= total_cost

        for _ in range(quantity):
            item = {
                "name": actual_name,
                "type": item_data["type"],
                "damage": item_data.get("damage"),
                "ac_bonus": item_data.get("ac_bonus"),
                "effect": item_data.get("effect")
            }
            character["inventory"].append(item)

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title="🛍️ Köp Genomfört!",
            description=f"**{character['name']}** köpte **{actual_name}** x{quantity}",
            color=discord.Color.green()
        )
        embed.add_field(name="💰 Kostnad", value=f"{total_cost}gp", inline=True)
        embed.add_field(name="💰 Kvar", value=f"{character['gold']}gp", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sell", description="Sälj ett item från din inventory")
    async def sell_item(self, interaction: discord.Interaction, item_name: str):
        """Säljer ett item från inventory."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        # Hitta item i inventory
        item_to_sell = None
        for item in character["inventory"]:
            if item["name"].lower() == item_name.lower():
                item_to_sell = item
                break

        if not item_to_sell:
            await interaction.response.send_message(
                f"❌ Du har inte **{item_name}** i din inventory!",
                ephemeral=True
            )
            return

        # Beräkna sell price (50% av original price)
        original_price = self.shop_items.get(item_to_sell["name"], {}).get("price", 1)
        sell_price = original_price // 2

        # Sälj item
        character["inventory"].remove(item_to_sell)
        character["gold"] += sell_price

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)

        embed = discord.Embed(
            title="💰 Försäljning Genomförd!",
            description=f"**{character['name']}** sålde **{item_to_sell['name']}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Fick", value=f"{sell_price}gp", inline=True)
        embed.add_field(name="💰 Totalt", value=f"{character['gold']}gp", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="use", description="Använd ett consumable item")
    async def use_item(self, interaction: discord.Interaction, item_name: str, target: Optional[discord.Member] = None):
        """Använder ett consumable item."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        # Hitta item i inventory
        item_to_use = None
        for item in character["inventory"]:
            if item["name"].lower() == item_name.lower() and item["type"] == "Consumable":
                item_to_use = item
                break

        if not item_to_use:
            await interaction.response.send_message(
                f"❌ Du har inte consumable **{item_name}** i din inventory!",
                ephemeral=True
            )
            return

        target_user = target or interaction.user
        target_char = self.get_character(str(target_user.id), str(interaction.guild.id))

        if not target_char:
            await interaction.response.send_message(
                f"❌ {target_user.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        # Använd item
        character["inventory"].remove(item_to_use)

        embed = discord.Embed(
            title=f"🧪 {character['name']} använder {item_to_use['name']}!",
            color=discord.Color.purple()
        )

        effect = item_to_use.get("effect", "Unknown effect")

        # Healing potion
        if "healing" in item_to_use["name"].lower():
            # Parse healing (t.ex. "2d4+2")
            import random
            dice_part, bonus = effect.split('+') if '+' in effect else (effect, '0')
            num_dice, die_size = dice_part.split('d')
            healing = sum(random.randint(1, int(die_size)) for _ in range(int(num_dice))) + int(bonus)

            old_hp = target_char["hp"]
            target_char["hp"] = min(target_char["hp"] + healing, target_char["max_hp"])
            actual_healing = target_char["hp"] - old_hp

            embed.add_field(name="💚 Healing", value=f"+{actual_healing} HP", inline=True)
            embed.add_field(name="❤️ HP", value=f"{old_hp} → {target_char['hp']}/{target_char['max_hp']}", inline=True)

        # Antidote
        elif "antidote" in item_to_use["name"].lower():
            if "Poisoned" in target_char.get("conditions", []):
                target_char["conditions"].remove("Poisoned")
                embed.add_field(name="🎭 Effect", value="Poisoned condition borttagen!", inline=False)
            else:
                embed.add_field(name="🎭 Effect", value="Ingen poisoned condition att ta bort", inline=False)

        # Other effects
        else:
            embed.add_field(name="✨ Effect", value=effect, inline=False)

        embed.description = f"På **{target_char['name']}**"

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)
        if target:
            self.save_character(str(target_user.id), str(interaction.guild.id), target_char)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trade", description="Ge ett item till en annan spelare")
    async def trade_item(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        item_name: str,
        gold_amount: int = 0
    ):
        """Tradear ett item eller guld till en annan spelare."""
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Du kan inte tradea med dig själv!", ephemeral=True)
            return

        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))
        target_char = self.get_character(str(target.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message("❌ Du har ingen karaktär!", ephemeral=True)
            return

        if not target_char:
            await interaction.response.send_message(f"❌ {target.display_name} har ingen karaktär!", ephemeral=True)
            return

        # Trade item
        item_to_trade = None
        if item_name.lower() != "none":
            for item in character["inventory"]:
                if item["name"].lower() == item_name.lower():
                    item_to_trade = item
                    break

            if not item_to_trade:
                await interaction.response.send_message(
                    f"❌ Du har inte **{item_name}** i din inventory!",
                    ephemeral=True
                )
                return

            character["inventory"].remove(item_to_trade)
            target_char["inventory"].append(item_to_trade)

        # Trade gold
        if gold_amount > 0:
            if character["gold"] < gold_amount:
                await interaction.response.send_message(
                    f"❌ Du har inte {gold_amount}gp! Du har {character['gold']}gp.",
                    ephemeral=True
                )
                return

            character["gold"] -= gold_amount
            target_char["gold"] += gold_amount

        self.save_character(str(interaction.user.id), str(interaction.guild.id), character)
        self.save_character(str(target.id), str(interaction.guild.id), target_char)

        embed = discord.Embed(
            title="🤝 Trade Genomförd!",
            description=f"**{character['name']}** → **{target_char['name']}**",
            color=discord.Color.blue()
        )

        if item_to_trade:
            embed.add_field(name="📦 Item", value=item_to_trade["name"], inline=True)
        if gold_amount > 0:
            embed.add_field(name="💰 Guld", value=f"{gold_amount}gp", inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ShopCog(bot))