# ==================== FUN.PY ====================
import random, discord
from discord.ext import commands
from discord import app_commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
    name="coinflip",
    description="Kasta ett mynt",
    extras={"cog": "Spel", "help_text": "Slumpa mellan KRONA och KLAVE. Bra för beslut eller tur."})
    async def coinflip(self, interaction: discord.Interaction):
        res = random.choice(["KLAVE", "KRONA"])
        emoji = "🪙" if res == "KRONA" else "🪙"
        embed = discord.Embed(title="🪙 Myntkast", description=f"{interaction.user.mention} Myntet landade på **{res}**!", color=0x00ff99)
        await interaction.response.send_message(embed=embed, delete_after=60)

    @app_commands.command(
    name="eightball",
    description="Fråga 8ball",
    extras={"cog": "Spel", "help_text": "Ställ en ja/nej-fråga och få ett slumpmässigt svar från 8ball."})
    async def eightball(self, interaction: discord.Interaction, fråga: str):
        svar = ["Ja, definitivt!", "Absolut!", "Nej.", "Mycket tveksamt.", "Fråga igen senare.", "Troligtvis.", "Ser bra ut.", "Jag vet inte ens vad du frågar om.", "Du har redan svaret inom dig.", "Det är skrivet i stjärnorna... kanske.", "Jag är en bot, inte en spåkula.", "100%... eller 0%. Svårt att säga.", "Du borde fokusera på något annat.", "Jag skulle säga ja, men jag ljuger ofta.", "Det är mer troligt än att vinna på lotto.", "Jag ser... en framtid... med pizza.", "Allt pekar på... att du borde gå och lägga dig."]
        embed = discord.Embed(title=f"{interaction.user.display_name}: {fråga}", description=f"🎱 {random.choice(svar)}", color=0x0099ff)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
    name="dice",
    description="Kasta tärning (ex: 2d20)",
    extras={"cog": "Spel", "help_text": "Exempel: `/dice 2d6` kastar två sexsidiga tärningar. Max 50 tärningar, 1000 sidor."})
    async def dice(self, interaction: discord.Interaction, dice: str = "1d20"):
        try:
            amount, sides = (map(int, dice.lower().split("d")) if "d" in dice.lower() else (1, int(dice)))

            max_amount = 50
            max_sides = 1000
            if amount > max_amount or amount <= 0 or sides <= 0 or sides > max_sides:
                raise ValueError(f"Max {max_amount}d{max_sides}")

            rolls = [random.randint(1, sides) for _ in range(amount)]
            total = sum(rolls)
            text = f"{interaction.user.mention} kastade **{amount}d{sides}** → `{', '.join(map(str, rolls))}` = **{total}** 🎲"

            embed = discord.Embed(title="🎲 Tärningskast", description=text, color=0x9966ff)
            await interaction.response.send_message(embed=embed, delete_after=60)
        except Exception as e:
            await interaction.response.send_message(f"❌ Felaktigt format: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))