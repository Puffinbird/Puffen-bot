import discord
from discord.ext import commands
from discord import app_commands

class HelpCog(commands.Cog):
    """Cog för hjälpkommandon."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Visa alla tillgängliga kommandon")
    async def help_command(self, interaction: discord.Interaction):
        """Visar alla tillgängliga kommandon."""

        embed = discord.Embed(
            title="🎲 Puffen-RPG - Hjälp",
            description="D&D - Alla kommandon",
            color=discord.Color.blue()
        )

        # Tärningar
        dice_commands = """
        `/roll <dice>` - Slå tärningar (1d20, 2d6+3, 1d20adv)
        `/stats` - Slå karaktärsstats (4d6 drop lowest)
        `/coinflip` - Kasta ett mynt
        """
        embed.add_field(name="🎲 Tärningar", value=dice_commands, inline=False)

        # Karaktärer
        char_commands = """
        `/createchar` - Skapa din karaktär
        `/char [target]` - Visa karaktär
        `/deletechar` - Ta bort din karaktär
        `/additem` - Lägg till item
        `/inventory [target]` - Visa inventory
        """
        embed.add_field(name="⚔️ Karaktärer", value=char_commands, inline=False)

        # Strid
        combat_commands = """
        `/initiative` - Slå initiative
        `/attack [target]` - Attackera med vapen
        `/heal <amount> [target]` - Heala
        `/addcondition <condition> [target]` - Lägg till condition
        `/removecondition <condition> [target]` - Ta bort condition
        `/conditions` - Visa alla conditions
        `/temphp <amount> [target]` - Lägg till temp HP
        """
        embed.add_field(name="⚔️ Strid", value=combat_commands, inline=False)

        # Spells
        spell_commands = """
        `/addspell <name> <level>` - Lägg till spell
        `/spellbook [target]` - Visa spellbook
        `/cast <spell_name> [level]` - Casta spell
        `/longrest` - Ta en long rest (återställ allt)
        `/shortrest [hit_dice]` - Ta en short rest (heala)
        """
        embed.add_field(name="✨ Spells", value=spell_commands, inline=False)

        # GM Kommandon
        gm_commands = """
        `/party` - Visa alla karaktärer
        `/damage <target> <amount>` - Ge skada till spelare
        `/sethp <target> <hp>` - Sätt HP
        `/givexp <target> <xp>` - Ge XP
        `/givegold <target> <gold>` - Ge guld
        `/giveitem <target> <name>` - Ge item
        `/createnpc <name>` - Skapa NPC
        `/createmonster <name>` - Skapa monster
        `/npcs` - Visa alla NPCs
        `/monsters` - Visa alla monsters
        `/damagenpc <name> <amount>` - Skada NPC/monster
        `/deletenpc <name>` - Ta bort NPC
        `/deletemonster <name>` - Ta bort monster
        """
        embed.add_field(name="🎮 GM Kommandon (Admin)", value=gm_commands, inline=False)

        embed.set_footer(text="Tips: Använd [target] för att välja en annan spelare, annars dig själv")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="guide", description="Guide för hur man spelar D&D med denna bot")
    async def guide(self, interaction: discord.Interaction):
        """Visar en guide för hur man använder boten."""

        embed = discord.Embed(
            title="📖 Puffen-RPG - Guide",
            description="Steg för steg guide för att spela D&D",
            color=discord.Color.gold()
        )

        step1 = """
        1️⃣ Använd `/stats` för att slå karaktärsstats
        2️⃣ Använd `/createchar` och fyll i dina stats
        3️⃣ Använd `/additem` för att lägga till vapen och rustning
        """
        embed.add_field(name="📝 Steg 1: Skapa Karaktär", value=step1, inline=False)

        step2 = """
        1️⃣ GM använder `/createnpc` eller `/createmonster`
        2️⃣ Alla slår `/initiative`
        3️⃣ Spelare använder `/attack` för att attackera
        4️⃣ GM använder `/damage` för att ge skada
        5️⃣ Använd `/heal` när ni behöver heala
        """
        embed.add_field(name="⚔️ Steg 2: Strid", value=step2, inline=False)

        step3 = """
        1️⃣ Spellcasters använder `/addspell` för att lägga till spells
        2️⃣ Använd `/cast` för att casta spells
        3️⃣ Använd `/longrest` för att återställa spell slots
        """
        embed.add_field(name="✨ Steg 3: Spells (Spellcasters)", value=step3, inline=False)

        step4 = """
        • `/addcondition` - Lägg till status effects (Poisoned, Stunned, etc.)
        • `/temphp` - Lägg till temporary HP
        • `/party` - Se hela gruppen
        • `/givexp` - GM ger XP efter strid
        • `/shop` - Köp vapen, rustning och potions
        • `/acceptquest` - Acceptera quests från GM
        • `/loot` - GM genererar random loot
        """
        embed.add_field(name="🎯 Extra Features", value=step4, inline=False)

        tips = """
        💡 Använd `/roll 1d20adv` för advantage
        💡 Använd `/roll 1d20dis` för disadvantage
        💡 Spara tid med `/shortrest` istället för att manuellt heala
        💡 GM kan använda `/damagenpc` för att skada monsters
        💡 Köp Healing Potions från `/shop` innan äventyr
        💡 Använd `/use Healing Potion` för att heala under strid
        💡 `/monsterloot` ger automatisk loot baserat på monster typ
        💡 Skapa treasure chests med `/treasure` som spelare kan hitta
        """
        embed.add_field(name="💡 Tips & Tricks", value=tips, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))