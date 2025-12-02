# ==================== QUOTES.PY ====================
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from utils_core import dm, logger

class QuotePaginator(discord.ui.View):
    def __init__(self, quotes):
        super().__init__(timeout=600)
        self.quotes = quotes
        self.page = 0
        self.per_page = 5   # <-- ändrat till 5 per sida
        self.max_page = (len(quotes) - 1) // self.per_page

    def get_embed(self):
        embed = discord.Embed(
            title=f"📜 Quotes (sida {self.page+1}/{self.max_page+1})",
            color=0x0099ff
        )
        for i, q in enumerate(self.quotes[self.page*self.per_page:(self.page+1)*self.per_page], start=self.page*self.per_page+1):
            embed.add_field(
                name=f"{i}.",
                value=f"\"{q['quote']}\" – {q['user']} – {q['date']}",
                inline=False
            )
        embed.set_footer(text=f"Totalt: {len(self.quotes)} citat")
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed())

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="addquote",
        description="Lägg till quote",
        extras={"cog": "Citat", "help_text": "Lägg till ett citat och vem som sa det (valfritt)."})
    async def add_quote(self, interaction: discord.Interaction, quote: str, author: str = None):
        if not author:
            author = interaction.user.display_name

        quotes = await dm.load_json("quotes", interaction.guild.id, [])
        quotes.append({
            "quote": quote,
            "user": author,
            "date": datetime.now().strftime("%d/%m/%y")
        })
        await dm.save_json("quotes", interaction.guild.id, quotes)

        embed = discord.Embed(
            title="✅ Quote tillagd",
            description=f"\"{quote}\" – {author} – {datetime.now().strftime('%d/%m/%y')}",
            color=0x33cc33
        )
        await interaction.response.send_message(embed=embed, delete_after=60)

    @app_commands.command(
        name="quotes",
        description="Visa quotes",
        extras={"cog": "Citat", "help_text": "Visar alla sparade citat med sidvisning."}
    )
    async def list_quotes(self, interaction: discord.Interaction):
        quotes = await dm.load_json("quotes", interaction.guild.id, [])
        if not quotes:
            await interaction.response.send_message("Inga quotes än.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=QuotePaginator(quotes).get_embed(),
            view=QuotePaginator(quotes)
        )

    @app_commands.command(
        name="delquote",
        description="Ta bort quote",
        extras={"cog": "Citat", "help_text": "Tar bort ett citat med angivet index. Endast admin."}
    )
    @app_commands.default_permissions(administrator=True)
    async def delete_quote(self, interaction: discord.Interaction, index: int):
        quotes = await dm.load_json("quotes", interaction.guild.id, [])
        if index < 1 or index > len(quotes):
            await interaction.response.send_message(f"❌ Ingen quote på plats {index}.", ephemeral=True)
            return

        target = quotes.pop(index - 1)
        await dm.save_json("quotes", interaction.guild.id, quotes)

        embed = discord.Embed(
            title="🗑️ Quote borttagen",
            description=f"\"{target['quote']}\" – {target['user']} – {target['date']}",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Quotes(bot))
