import discord
from discord import app_commands
from discord.ext import commands
import random
import math

class RPSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Spela Sten Sax Påse mot en annan användare")
    @app_commands.describe(opponent="Användaren att utmana", best_of="Bäst av hur många spel? (1,3,5)")
    @app_commands.choices(best_of=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="3", value=3),
        app_commands.Choice(name="5", value=5),
    ])
    async def rps(self, interaction: discord.Interaction, opponent: discord.Member, best_of: int = 1):
        if opponent == interaction.user:
            await interaction.response.send_message("Kan inte spela mot dig själv.", ephemeral=True)
            return
        if opponent.bot:
            await interaction.response.send_message("Kan inte spela mot bottar.", ephemeral=True)
            return

        view = RPSView(interaction.user, opponent, best_of)
        await interaction.response.send_message(f"{interaction.user.mention} utmanar {opponent.mention} till Sten Sax Påse! Välj ditt drag.", view=view)

class RPSView(discord.ui.View):
    def __init__(self, player1: discord.Member, player2: discord.Member, best_of: int):
        super().__init__(timeout=300)
        self.player1 = player1
        self.player2 = player2
        self.best_of = best_of
        self.wins_needed = math.ceil(best_of / 2)
        self.scores = {player1.id: 0, player2.id: 0}
        self.choices = {}
        self.current_round = 1
        self.add_buttons()

    def add_buttons(self):
        self.add_item(RPSButton("Sten", self))
        self.add_item(RPSButton("Sax", self))
        self.add_item(RPSButton("Påse", self))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user in (self.player1, self.player2) and interaction.user.id not in self.choices

    async def on_timeout(self):
        await self.message.edit(content="Spelet tog för lång tid.", view=None)

    async def resolve_round(self):
        p1_choice = self.choices[self.player1.id]
        p2_choice = self.choices[self.player2.id]
        if p1_choice == p2_choice:
            result = "Oavgjort!"
        elif (p1_choice == "Sten" and p2_choice == "Sax") or \
             (p1_choice == "Sax" and p2_choice == "Påse") or \
             (p1_choice == "Påse" and p2_choice == "Sten"):
            result = f"{self.player1.mention} vinner rundan!"
            self.scores[self.player1.id] += 1
        else:
            result = f"{self.player2.mention} vinner rundan!"
            self.scores[self.player2.id] += 1

        score_text = f"Poäng: {self.player1.mention} {self.scores[self.player1.id]} - {self.player2.mention} {self.scores[self.player2.id]}"

        if self.scores[self.player1.id] >= self.wins_needed:
            final = f"{self.player1.mention} vinner matchen!"
            await self.message.edit(content=f"{result}\n{score_text}\n{final}", view=None)
            self.stop()
            return
        elif self.scores[self.player2.id] >= self.wins_needed:
            final = f"{self.player2.mention} vinner matchen!"
            await self.message.edit(content=f"{result}\n{score_text}\n{final}", view=None)
            self.stop()
            return

        self.choices = {}
        self.current_round += 1
        await self.message.edit(content=f"{result}\n{score_text}\nNästa runda: Välj ditt drag.", view=self)

class RPSButton(discord.ui.Button):
    def __init__(self, label: str, view: RPSView):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        self.view.choices[interaction.user.id] = self.label
        await interaction.response.send_message(f"Du valde {self.label}.", ephemeral=True)
        if len(self.view.choices) == 2:
            await self.view.resolve_round()

async def setup(bot):
    await bot.add_cog(RPSCog(bot))