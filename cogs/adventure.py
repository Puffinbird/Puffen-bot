import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
from typing import Optional

class AdventureGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "player_data.json"
        self.players = self.load_players()

        # Game data
        self.weapons = {
            "träsvärd": {"damage": 5, "price": 0},
            "järnsvärd": {"damage": 15, "price": 50},
            "stålsvärd": {"damage": 25, "price": 150},
            "diamantsvärd": {"damage": 40, "price": 300}
        }

        self.armor = {
            "läderpansar": {"defense": 3, "price": 0},
            "järnpansar": {"defense": 10, "price": 60},
            "stålpansar": {"defense": 18, "price": 180},
            "diamantpansar": {"defense": 30, "price": 350}
        }

        self.enemies = {
            "goblin": {"hp": 30, "damage": 8, "gold": 20, "xp": 15},
            "ork": {"hp": 50, "damage": 15, "gold": 40, "xp": 30},
            "troll": {"hp": 80, "damage": 25, "gold": 70, "xp": 50},
            "drake": {"hp": 150, "damage": 40, "gold": 200, "xp": 100},
            "demon lord": {"hp": 300, "damage": 60, "gold": 500, "xp": 250}
        }

        self.items = {
            "läkande dryck": {"heal": 30, "price": 25},
            "stor läkande dryck": {"heal": 60, "price": 50},
            "styrkedryck": {"damage_boost": 10, "duration": 3, "price": 40}
        }

    def load_players(self):
        """Ladda spelardata från fil"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    return {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Error loading player data: {e}")
                return {}
        return {}

    def save_players(self):
        """Spara spelardata till fil"""
        try:
            # Convert integer keys to strings for JSON
            data = {str(k): v for k, v in self.players.items()}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving player data: {e}")

    def create_player(self, user_id: int, username: str):
        """Skapa en ny spelare"""
        self.players[user_id] = {
            "name": username,
            "hp": 100,
            "max_hp": 100,
            "level": 1,
            "xp": 0,
            "xp_needed": 100,
            "gold": 50,
            "weapon": "träsvärd",
            "armor": "läderpansar",
            "inventory": {"läkande dryck": 2},
            "in_combat": False,
            "objective_progress": 0,
            "objective_complete": False,
            "buffs": {},
            "total_kills": 0,
            "deaths": 0
        }
        self.save_players()

    def get_player_stats(self, user_id: int) -> discord.Embed:
        """Hämta spelarens stats"""
        p = self.players[user_id]
        weapon_dmg = self.weapons[p["weapon"]]["damage"]
        armor_def = self.armor[p["armor"]]["defense"]

        embed = discord.Embed(title=f"⚔️ {p['name']}'s Äventyr", color=discord.Color.blue())
        embed.add_field(name="❤️ HP", value=f"{p['hp']}/{p['max_hp']}", inline=True)
        embed.add_field(name="⭐ Level", value=str(p['level']), inline=True)
        embed.add_field(name="✨ XP", value=f"{p['xp']}/{p['xp_needed']}", inline=True)
        embed.add_field(name="💰 Guld", value=str(p['gold']), inline=True)
        embed.add_field(name="⚔️ Vapen", value=f"{p['weapon']} ({weapon_dmg} skada)", inline=True)
        embed.add_field(name="🛡️ Rustning", value=f"{p['armor']} ({armor_def} försvar)", inline=True)
        embed.add_field(name="📊 Statistik", value=f"💀 Kills: {p['total_kills']} | ☠️ Deaths: {p['deaths']}", inline=False)

        # Objective status
        if not p['objective_complete']:
            embed.add_field(name="🎯 Uppdrag", value=f"Besegra Demon Lord! (Fiender besegrade: {p['objective_progress']}/10)", inline=False)
        else:
            embed.add_field(name="🎯 Uppdrag", value="✅ Kompletterat! Du besegrade Demon Lord!", inline=False)

        return embed

    @app_commands.command(name="start", description="Starta ditt äventyr!")
    async def start(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.players:
            await interaction.response.send_message("Du har redan startat ditt äventyr! Använd `/stats` för att se din progress.", ephemeral=True)
            return

        self.create_player(user_id, interaction.user.name)
        embed = discord.Embed(
            title="🗡️ Välkommen Äventyrare!",
            description=f"Välkommen {interaction.user.name}! Ditt äventyr börjar nu!\n\nEtt mörkt hot har lagt sig över landet - Demon Lord terroriserar byarna.\n\n**Ditt uppdrag:** Besegra 10 fiender och möt sedan Demon Lord i en episk strid!\n\nDin progress sparas automatiskt mellan sessions!",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 Kommandon", value="`/explore` - Utforska och möt fiender\n`/stats` - Se din karaktär\n`/shop` - Handla utrustning", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="Se dina stats och inventory")
    async def stats(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        embed = self.get_player_stats(user_id)

        # Lägg till inventory
        inv = self.players[user_id]["inventory"]
        if inv:
            inv_text = "\n".join([f"• {item}: {count}x" for item, count in inv.items() if count > 0])
            if inv_text:
                embed.add_field(name="🎒 Inventory", value=inv_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="explore", description="Utforska och möt fiender!")
    async def explore(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]
        if p["in_combat"]:
            await interaction.response.send_message("Du är redan i strid!", ephemeral=True)
            return

        # Check if objective is complete and spawn Demon Lord
        if p["objective_progress"] >= 10 and not p["objective_complete"]:
            enemy_type = "demon lord"
            embed = discord.Embed(
                title="👹 DEMON LORD HAR DYKT UPP!",
                description="Den fruktade Demon Lord står framför dig! Detta är den slutliga striden!",
                color=discord.Color.dark_red()
            )
        else:
            # Random enemy based on level
            enemy_pool = ["goblin", "ork"]
            if p["level"] >= 3:
                enemy_pool.append("troll")
            if p["level"] >= 5:
                enemy_pool.append("drake")

            enemy_type = random.choice(enemy_pool)
            embed = discord.Embed(
                title=f"⚔️ En vild {enemy_type.upper()} dyker upp!",
                description=f"Förbered dig för strid!",
                color=discord.Color.orange()
            )

        p["in_combat"] = True
        p["current_enemy"] = {
            "type": enemy_type,
            "hp": self.enemies[enemy_type]["hp"],
            "max_hp": self.enemies[enemy_type]["hp"]
        }
        self.save_players()

        enemy = p["current_enemy"]
        embed.add_field(name="🩸 Fiendens HP", value=f"{enemy['hp']}/{enemy['max_hp']}", inline=True)
        embed.add_field(name="💥 Fiendens Skada", value=str(self.enemies[enemy_type]["damage"]), inline=True)
        embed.set_footer(text="Använd /attack för att attackera eller /use för att använda items!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="attack", description="Attackera fienden!")
    async def attack(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]
        if not p["in_combat"]:
            await interaction.response.send_message("Du är inte i strid! Använd `/explore`", ephemeral=True)
            return

        enemy = p["current_enemy"]
        enemy_type = enemy["type"]

        # Player attacks
        weapon_dmg = self.weapons[p["weapon"]]["damage"]
        buff_dmg = p["buffs"].get("damage_boost", 0)
        total_dmg = weapon_dmg + buff_dmg + random.randint(-3, 5)
        enemy["hp"] -= total_dmg

        embed = discord.Embed(title="⚔️ Strid!", color=discord.Color.red())
        embed.add_field(name="Din attack", value=f"Du träffar {enemy_type} för **{total_dmg}** skada!", inline=False)

        # Check if enemy is dead
        if enemy["hp"] <= 0:
            gold_reward = self.enemies[enemy_type]["gold"]
            xp_reward = self.enemies[enemy_type]["xp"]
            p["gold"] += gold_reward
            p["xp"] += xp_reward
            p["in_combat"] = False
            p["total_kills"] += 1

            # Check if it's Demon Lord
            if enemy_type == "demon lord":
                p["objective_complete"] = True
                embed.add_field(name="🎉 SEGER!", value=f"Du besegrade {enemy_type.upper()}!\n\n🏆 **DU KLARADE UPPDRAGET!** 🏆\n\n+{gold_reward}💰 guld\n+{xp_reward}✨ XP", inline=False)
            else:
                p["objective_progress"] += 1
                embed.add_field(name="🎉 Seger!", value=f"Du besegrade {enemy_type}!\n+{gold_reward}💰 guld\n+{xp_reward}✨ XP\n\nFiender besegrade: {p['objective_progress']}/10", inline=False)

            # Level up check
            while p["xp"] >= p["xp_needed"]:
                p["level"] += 1
                p["xp"] -= p["xp_needed"]
                p["xp_needed"] = int(p["xp_needed"] * 1.5)
                p["max_hp"] += 20
                p["hp"] = p["max_hp"]
                embed.add_field(name="⭐ LEVEL UP!", value=f"Du är nu level {p['level']}!\n+20 Max HP", inline=False)

            # Update buffs
            for buff in list(p["buffs"].keys()):
                p["buffs"][buff] -= 1
                if p["buffs"][buff] <= 0:
                    del p["buffs"][buff]

            self.save_players()
            await interaction.response.send_message(embed=embed)
            return

        # Enemy attacks back
        enemy_dmg = self.enemies[enemy_type]["damage"]
        armor_def = self.armor[p["armor"]]["defense"]
        actual_dmg = max(1, enemy_dmg - armor_def + random.randint(-2, 3))
        p["hp"] -= actual_dmg

        embed.add_field(name="Fiendens attack", value=f"{enemy_type.capitalize()} träffar dig för **{actual_dmg}** skada!", inline=False)
        embed.add_field(name="🩸 Ditt HP", value=f"{p['hp']}/{p['max_hp']}", inline=True)
        embed.add_field(name="🩸 Fiendens HP", value=f"{enemy['hp']}/{enemy['max_hp']}", inline=True)

        # Check if player is dead
        if p["hp"] <= 0:
            p["hp"] = p["max_hp"]
            p["gold"] = max(0, p["gold"] - 20)
            p["in_combat"] = False
            p["deaths"] += 1
            embed.add_field(name="💀 Du dog!", value="Du förlorade 20 guld och återupplivades.", inline=False)

        # Update buffs
        for buff in list(p["buffs"].keys()):
            p["buffs"][buff] -= 1
            if p["buffs"][buff] <= 0:
                del p["buffs"][buff]

        self.save_players()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="Handla vapen, rustning och items")
    async def shop(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]

        embed = discord.Embed(
            title="🏪 Butiken",
            description=f"Välkommen till butiken!\n💰 Ditt guld: **{p['gold']}**",
            color=discord.Color.gold()
        )

        # Weapons
        weapon_text = "\n".join([f"• {name}: {data['damage']} skada - {data['price']}💰" for name, data in self.weapons.items()])
        embed.add_field(name="⚔️ Vapen", value=weapon_text, inline=False)

        # Armor
        armor_text = "\n".join([f"• {name}: {data['defense']} försvar - {data['price']}💰" for name, data in self.armor.items()])
        embed.add_field(name="🛡️ Rustning", value=armor_text, inline=False)

        # Items
        items_text = "\n".join([f"• {name}: {data.get('heal', data.get('damage_boost', 0))} {'HP' if 'heal' in data else 'skada'} - {data['price']}💰" for name, data in self.items.items()])
        embed.add_field(name="🧪 Items", value=items_text, inline=False)

        embed.set_footer(text="Använd /buy <item namn> för att köpa!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Köp items från butiken")
    async def buy(self, interaction: discord.Interaction, item: str):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]
        item = item.lower()

        # Check all categories
        if item in self.weapons:
            price = self.weapons[item]["price"]
            if p["gold"] >= price:
                p["gold"] -= price
                p["weapon"] = item
                self.save_players()
                await interaction.response.send_message(f"✅ Du köpte {item}! Ditt guld: {p['gold']}💰")
            else:
                await interaction.response.send_message(f"❌ Du har inte råd! Pris: {price}💰 (Du har: {p['gold']}💰)", ephemeral=True)

        elif item in self.armor:
            price = self.armor[item]["price"]
            if p["gold"] >= price:
                p["gold"] -= price
                p["armor"] = item
                self.save_players()
                await interaction.response.send_message(f"✅ Du köpte {item}! Ditt guld: {p['gold']}💰")
            else:
                await interaction.response.send_message(f"❌ Du har inte råd! Pris: {price}💰 (Du har: {p['gold']}💰)", ephemeral=True)

        elif item in self.items:
            price = self.items[item]["price"]
            if p["gold"] >= price:
                p["gold"] -= price
                p["inventory"][item] = p["inventory"].get(item, 0) + 1
                self.save_players()
                await interaction.response.send_message(f"✅ Du köpte {item}! Ditt guld: {p['gold']}💰")
            else:
                await interaction.response.send_message(f"❌ Du har inte råd! Pris: {price}💰 (Du har: {p['gold']}💰)", ephemeral=True)

        else:
            await interaction.response.send_message("❌ Item finns inte i butiken! Kolla `/shop` för att se vad som finns.", ephemeral=True)

    @app_commands.command(name="use", description="Använd ett item från ditt inventory")
    async def use_item(self, interaction: discord.Interaction, item: str):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]
        item = item.lower()

        if item not in p["inventory"] or p["inventory"][item] <= 0:
            await interaction.response.send_message("❌ Du har inte detta item!", ephemeral=True)
            return

        if item not in self.items:
            await interaction.response.send_message("❌ Detta item kan inte användas!", ephemeral=True)
            return

        item_data = self.items[item]
        p["inventory"][item] -= 1

        if "heal" in item_data:
            heal_amount = min(item_data["heal"], p["max_hp"] - p["hp"])
            p["hp"] += heal_amount
            self.save_players()
            await interaction.response.send_message(f"✅ Du använde {item} och återfick {heal_amount} HP! (HP: {p['hp']}/{p['max_hp']})")

        elif "damage_boost" in item_data:
            p["buffs"]["damage_boost"] = item_data["damage_boost"]
            self.save_players()
            await interaction.response.send_message(f"✅ Du använde {item}! +{item_data['damage_boost']} skada i {item_data['duration']} rundor!")

    @app_commands.command(name="heal", description="Läk dig själv (kostar 15 guld)")
    async def heal(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har inte startat ännu! Använd `/start`", ephemeral=True)
            return

        p = self.players[user_id]

        if p["hp"] >= p["max_hp"]:
            await interaction.response.send_message("❌ Du har redan full HP!", ephemeral=True)
            return

        heal_cost = 15
        if p["gold"] < heal_cost:
            await interaction.response.send_message(f"❌ Du har inte råd! Kostnad: {heal_cost}💰 (Du har: {p['gold']}💰)", ephemeral=True)
            return

        p["gold"] -= heal_cost
        p["hp"] = p["max_hp"]
        self.save_players()
        await interaction.response.send_message(f"✨ Du läkte dig själv till full HP! (HP: {p['hp']}/{p['max_hp']}) | -{heal_cost}💰")

    @app_commands.command(name="leaderboard", description="Se topplistan!")
    async def leaderboard(self, interaction: discord.Interaction):
        if not self.players:
            await interaction.response.send_message("Inga spelare har startat ännu!", ephemeral=True)
            return

        # Sort by level, then by xp
        sorted_players = sorted(
            self.players.items(),
            key=lambda x: (x[1]["level"], x[1]["xp"], x[1]["total_kills"]),
            reverse=True
        )[:10]

        embed = discord.Embed(title="🏆 Topplista", color=discord.Color.gold())

        leaderboard_text = ""
        for idx, (user_id, data) in enumerate(sorted_players, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            leaderboard_text += f"{medal} **{data['name']}** - Lvl {data['level']} | {data['total_kills']} kills\n"

        embed.description = leaderboard_text
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset", description="Återställ din karaktär (PERMANENT!)")
    async def reset(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.players:
            await interaction.response.send_message("Du har ingen karaktär att återställa!", ephemeral=True)
            return

        del self.players[user_id]
        self.save_players()
        await interaction.response.send_message("🔄 Din karaktär har återställts! Använd `/start` för att börja om.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdventureGame(bot))