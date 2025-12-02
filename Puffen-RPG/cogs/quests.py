import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from config import DATA_FILE
import json
import os

class QuestsCog(commands.Cog):
    """Cog för quest tracking och hantering."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = DATA_FILE
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Initiera quests om det inte finns
                if 'quests' not in data:
                    data['quests'] = {}
                return data
        return {"characters": {}, "quests": {}}

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

    @app_commands.command(name="createquest", description="[GM] Skapa en quest")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_quest(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str,
        xp_reward: int = 0,
        gold_reward: int = 0,
        difficulty: Literal["Easy", "Medium", "Hard", "Deadly"] = "Medium"
    ):
        """[GM] Skapar en quest."""
        quest_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"

        if quest_id in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{name}** finns redan!",
                ephemeral=True
            )
            return

        quest = {
            "name": name,
            "description": description,
            "xp_reward": xp_reward,
            "gold_reward": gold_reward,
            "difficulty": difficulty,
            "status": "Available",
            "guild_id": str(interaction.guild.id),
            "accepted_by": [],
            "completed_by": [],
            "objectives": []
        }

        self.data["quests"][quest_id] = quest
        self.save_data()

        difficulty_colors = {
            "Easy": discord.Color.green(),
            "Medium": discord.Color.yellow(),
            "Hard": discord.Color.orange(),
            "Deadly": discord.Color.red()
        }

        embed = discord.Embed(
            title=f"📜 Quest Skapad: {name}",
            description=description,
            color=difficulty_colors.get(difficulty, discord.Color.blue())
        )
        embed.add_field(name="⚔️ Difficulty", value=difficulty, inline=True)
        embed.add_field(name="⭐ XP Reward", value=f"{xp_reward} XP", inline=True)
        embed.add_field(name="💰 Gold Reward", value=f"{gold_reward} gp", inline=True)
        embed.set_footer(text="Spelare kan acceptera med /acceptquest")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addobjective", description="[GM] Lägg till ett objective till en quest")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_objective(
        self,
        interaction: discord.Interaction,
        quest_name: str,
        objective: str
    ):
        """[GM] Lägger till ett objective till en quest."""
        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest = self.data["quests"][quest_id]
        quest["objectives"].append({"text": objective, "completed": False})
        self.save_data()

        await interaction.response.send_message(
            f"✅ Objective tillagt till **{quest['name']}**: {objective}"
        )

    @app_commands.command(name="quests", description="Visa alla tillgängliga quests")
    async def show_quests(
        self,
        interaction: discord.Interaction,
        filter: Literal["All", "Available", "Active", "Completed"] = "All"
    ):
        """Visar alla quests."""
        guild_quests = {k: v for k, v in self.data["quests"].items()
                       if v.get("guild_id") == str(interaction.guild.id)}

        if not guild_quests:
            await interaction.response.send_message("❌ Inga quests finns i denna server!", ephemeral=True)
            return

        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        embed = discord.Embed(
            title=f"📜 Quests - {interaction.guild.name}",
            description=f"Filter: {filter}",
            color=discord.Color.blue()
        )

        difficulty_icons = {
            "Easy": "🟢",
            "Medium": "🟡",
            "Hard": "🟠",
            "Deadly": "🔴"
        }

        for quest_id, quest in guild_quests.items():
            # Filter logic
            if filter == "Available" and quest["status"] != "Available":
                continue
            if filter == "Active" and (not character or str(interaction.user.id) not in quest["accepted_by"]):
                continue
            if filter == "Completed" and (not character or str(interaction.user.id) not in quest["completed_by"]):
                continue

            # Build quest info
            quest_info = f"*{quest['description']}*\n\n"
            quest_info += f"{difficulty_icons.get(quest['difficulty'], '⚪')} **{quest['difficulty']}** | "
            quest_info += f"⭐ {quest['xp_reward']} XP | 💰 {quest['gold_reward']} gp\n"

            # Objectives
            if quest["objectives"]:
                quest_info += "\n**Objectives:**\n"
                for i, obj in enumerate(quest["objectives"], 1):
                    status = "✅" if obj["completed"] else "⬜"
                    quest_info += f"{status} {i}. {obj['text']}\n"

            # Status
            if character and str(interaction.user.id) in quest["completed_by"]:
                quest_info += "\n🏆 **COMPLETED**"
            elif character and str(interaction.user.id) in quest["accepted_by"]:
                quest_info += "\n📌 **ACTIVE**"
            else:
                quest_info += f"\n📜 **{quest['status']}**"

            embed.add_field(name=f"📜 {quest['name']}", value=quest_info, inline=False)

        if len(embed.fields) == 0:
            embed.description = f"Inga quests matchar filter: {filter}"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="acceptquest", description="Acceptera en quest")
    async def accept_quest(self, interaction: discord.Interaction, quest_name: str):
        """Accepterar en quest."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär! Skapa en med `/createchar`",
                ephemeral=True
            )
            return

        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest = self.data["quests"][quest_id]

        if str(interaction.user.id) in quest["accepted_by"]:
            await interaction.response.send_message(
                f"❌ Du har redan accepterat **{quest['name']}**!",
                ephemeral=True
            )
            return

        if str(interaction.user.id) in quest["completed_by"]:
            await interaction.response.send_message(
                f"❌ Du har redan slutfört **{quest['name']}**!",
                ephemeral=True
            )
            return

        quest["accepted_by"].append(str(interaction.user.id))
        self.save_data()

        embed = discord.Embed(
            title=f"📜 Quest Accepterad!",
            description=f"**{character['name']}** har accepterat **{quest['name']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 Description", value=quest['description'], inline=False)

        if quest["objectives"]:
            obj_text = "\n".join([f"{i}. {obj['text']}" for i, obj in enumerate(quest["objectives"], 1)])
            embed.add_field(name="🎯 Objectives", value=obj_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="completeobjective", description="[GM] Markera ett objective som slutfört")
    @app_commands.checks.has_permissions(administrator=True)
    async def complete_objective(
        self,
        interaction: discord.Interaction,
        quest_name: str,
        objective_number: int
    ):
        """[GM] Markerar ett objective som slutfört."""
        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest = self.data["quests"][quest_id]

        if objective_number < 1 or objective_number > len(quest["objectives"]):
            await interaction.response.send_message(
                f"❌ Objective {objective_number} finns inte! Quest har {len(quest['objectives'])} objectives.",
                ephemeral=True
            )
            return

        quest["objectives"][objective_number - 1]["completed"] = True
        self.save_data()

        await interaction.response.send_message(
            f"✅ Objective {objective_number} slutfört för **{quest['name']}**!"
        )

    @app_commands.command(name="completequest", description="[GM] Markera en quest som slutförd för en spelare")
    @app_commands.checks.has_permissions(administrator=True)
    async def complete_quest(
        self,
        interaction: discord.Interaction,
        quest_name: str,
        player: discord.Member
    ):
        """[GM] Markerar en quest som slutförd och ger rewards."""
        character = self.get_character(str(player.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                f"❌ {player.display_name} har ingen karaktär!",
                ephemeral=True
            )
            return

        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest = self.data["quests"][quest_id]

        if str(player.id) in quest["completed_by"]:
            await interaction.response.send_message(
                f"❌ {player.display_name} har redan slutfört **{quest['name']}**!",
                ephemeral=True
            )
            return

        # Mark as completed
        if str(player.id) not in quest["completed_by"]:
            quest["completed_by"].append(str(player.id))
        if str(player.id) in quest["accepted_by"]:
            quest["accepted_by"].remove(str(player.id))

        # Give rewards
        character["xp"] += quest["xp_reward"]
        character["gold"] += quest["gold_reward"]

        self.save_character(str(player.id), str(interaction.guild.id), character)
        self.save_data()

        embed = discord.Embed(
            title=f"🏆 Quest Slutförd!",
            description=f"**{character['name']}** slutförde **{quest['name']}**!",
            color=discord.Color.gold()
        )
        embed.add_field(name="⭐ XP Earned", value=f"+{quest['xp_reward']} XP (Totalt: {character['xp']})", inline=True)
        embed.add_field(name="💰 Gold Earned", value=f"+{quest['gold_reward']} gp (Totalt: {character['gold']})", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="abandonquest", description="Avbryt en quest")
    async def abandon_quest(self, interaction: discord.Interaction, quest_name: str):
        """Avbryter en quest."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär!",
                ephemeral=True
            )
            return

        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest = self.data["quests"][quest_id]

        if str(interaction.user.id) not in quest["accepted_by"]:
            await interaction.response.send_message(
                f"❌ Du har inte accepterat **{quest['name']}**!",
                ephemeral=True
            )
            return

        quest["accepted_by"].remove(str(interaction.user.id))
        self.save_data()

        await interaction.response.send_message(
            f"✅ Du har avbrutit **{quest['name']}**"
        )

    @app_commands.command(name="deletequest", description="[GM] Ta bort en quest")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_quest(self, interaction: discord.Interaction, quest_name: str):
        """[GM] Tar bort en quest."""
        quest_id = f"{interaction.guild.id}_{quest_name.lower().replace(' ', '_')}"

        if quest_id not in self.data["quests"]:
            await interaction.response.send_message(
                f"❌ Quest **{quest_name}** finns inte!",
                ephemeral=True
            )
            return

        quest_name_actual = self.data["quests"][quest_id]["name"]
        del self.data["quests"][quest_id]
        self.save_data()

        await interaction.response.send_message(f"✅ Quest **{quest_name_actual}** har tagits bort!")

    @app_commands.command(name="myquests", description="Visa dina aktiva quests")
    async def my_quests(self, interaction: discord.Interaction):
        """Visar dina aktiva quests."""
        character = self.get_character(str(interaction.user.id), str(interaction.guild.id))

        if not character:
            await interaction.response.send_message(
                "❌ Du har ingen karaktär!",
                ephemeral=True
            )
            return

        active_quests = []
        for quest_id, quest in self.data["quests"].items():
            if str(interaction.user.id) in quest["accepted_by"]:
                active_quests.append(quest)

        if not active_quests:
            await interaction.response.send_message(
                "📜 Du har inga aktiva quests! Använd `/quests` för att se tillgängliga quests.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📜 {character['name']}'s Active Quests",
            description=f"Du har {len(active_quests)} aktiva quest(s)",
            color=discord.Color.blue()
        )

        for quest in active_quests:
            quest_info = f"*{quest['description']}*\n\n"

            # Progress
            if quest["objectives"]:
                completed = sum(1 for obj in quest["objectives"] if obj["completed"])
                total = len(quest["objectives"])
                progress = "█" * completed + "░" * (total - completed)
                quest_info += f"**Progress:** {progress} ({completed}/{total})\n"

                quest_info += "\n**Objectives:**\n"
                for i, obj in enumerate(quest["objectives"], 1):
                    status = "✅" if obj["completed"] else "⬜"
                    quest_info += f"{status} {i}. {obj['text']}\n"

            quest_info += f"\n**Rewards:** ⭐ {quest['xp_reward']} XP | 💰 {quest['gold_reward']} gp"

            embed.add_field(name=f"📜 {quest['name']}", value=quest_info, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(QuestsCog(bot))