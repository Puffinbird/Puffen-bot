# ==================== ROLES.PY ====================
import discord
from discord.ext import commands
from discord import app_commands
from utils_core import dm, logger

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _update_menu(self, guild: discord.Guild):
        """Uppdatera rollmenyns embed och reaktioner automatiskt."""
        menu = await dm.load_json("role_menu", guild.id, {})
        if not menu or "message_id" not in menu:
            return

        mapping = await dm.load_json("reaction_roles", guild.id, {})
        if not mapping:
            return

        channel = None
        # Hämta meddelandet
        for ch in guild.text_channels:
            try:
                msg = await ch.fetch_message(menu["message_id"])
                channel = ch
                break
            except Exception:
                continue

        if not channel:
            return

        embed = discord.Embed(title="Välj dina roller!", color=0x00ff00)
        embed.description = "Reagera med rätt emoji för att få rollen!\n\n" + \
            "\n".join(f"{e} <@&{r}>" for e, r in mapping.items())

        try:
            await msg.edit(embed=embed)
            # Rensa gamla reaktioner och lägg till aktuella
            await msg.clear_reactions()
            for emoji in mapping.keys():
                await msg.add_reaction(emoji)
        except Exception as e:
            logger.error(f"Kunde inte uppdatera rollmenyn: {e}")

    @app_commands.command(
        name="rollmeny",
        description="Skapa rollmeny",
        extras={"cog": "Roller", "help_text": "Skapar ett meddelande där användare kan välja roller via emoji."}
    )
    @app_commands.default_permissions(administrator=True)
    async def rollmeny(self, interaction: discord.Interaction):
        mapping = await dm.load_json("reaction_roles", interaction.guild.id, {})
        if not mapping:
            await interaction.response.send_message("❌ Inga kopplingar än. Lägg till med `/setrole`", ephemeral=True)
            return

        embed = discord.Embed(title="Välj dina roller!", color=0x00ff00)
        embed.description = "Reagera med rätt emoji för att få rollen!\n\n" + \
            "\n".join(f"{e} <@&{r}>" for e, r in mapping.items())

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        for emoji in mapping.keys():
            try:
                await msg.add_reaction(emoji)
            except Exception as e:
                logger.warning(f"Kunde inte lägga till reaktion {emoji}: {e}")

        await dm.save_json("role_menu", interaction.guild.id, {"message_id": msg.id})

    @app_commands.command(
        name="setrole",
        description="Koppla emoji → roll",
        extras={"cog": "Roller", "help_text": "Kopplar en emoji till en roll. Används i rollmenyn."}
    )
    @app_commands.default_permissions(administrator=True)
    async def setrole(self, interaction: discord.Interaction, emoji: str, role: discord.Role):
        mapping = await dm.load_json("reaction_roles", interaction.guild.id, {})
        mapping[emoji] = role.id
        await dm.save_json("reaction_roles", interaction.guild.id, mapping)
        await interaction.response.send_message(f"✅ {emoji} → {role.mention}", ephemeral=True)
        await self._update_menu(interaction.guild)

    @app_commands.command(
        name="deleterole",
        description="Ta bort emoji → roll",
        extras={"cog": "Roller", "help_text": "Tar bort en emoji-koppling från rollmenyn."}
    )
    @app_commands.default_permissions(administrator=True)
    async def delete_role(self, interaction: discord.Interaction, emoji: str):
        mapping = await dm.load_json("reaction_roles", interaction.guild.id, {})
        if emoji not in mapping:
            await interaction.response.send_message(f"❌ Ingen koppling för {emoji}", ephemeral=True)
            return

        removed = mapping.pop(emoji)
        await dm.save_json("reaction_roles", interaction.guild.id, mapping)
        await interaction.response.send_message(f"🗑️ Tog bort {emoji} → <@&{removed}>", ephemeral=True)
        await self._update_menu(interaction.guild)

    @app_commands.command(
        name="listroles",
        description="Visa roller",
        extras={"cog": "Roller", "help_text": "Visar alla emoji → roll-kopplingar."}
    )
    async def listroles(self, interaction: discord.Interaction):
        mapping = await dm.load_json("reaction_roles", interaction.guild.id, {})
        if not mapping:
            await interaction.response.send_message("Inga kopplingar än.", ephemeral=True)
            return

        embed = discord.Embed(title="Emoji → Roll", color=0x0099ff)
        for e, r in mapping.items():
            embed.add_field(name=e, value=f"<@&{r}>", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member and payload.member.bot:
            return

        menu = await dm.load_json("role_menu", payload.guild_id, {})
        if not menu or payload.message_id != menu.get("message_id"):
            return

        mapping = await dm.load_json("reaction_roles", payload.guild_id, {})
        emoji_str = str(payload.emoji)

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if emoji_str in mapping:
            role = guild.get_role(mapping[emoji_str])
            member = payload.member or guild.get_member(payload.user_id)

            if role and member:
                try:
                    await member.add_roles(role)
                    logger.info(f"Lade till roll {role.name} till {member.display_name}")
                except Exception as e:
                    logger.error(f"Kunde inte lägga till roll {role.name}: {e}")
        else:
            try:
                await message.remove_reaction(payload.emoji, payload.member)
                logger.info(f"Tog bort ogiltig reaktion {emoji_str} från {payload.member.display_name}")
            except Exception as e:
                logger.warning(f"Kunde inte ta bort ogiltig reaktion {emoji_str}: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        menu = await dm.load_json("role_menu", payload.guild_id, {})
        if not menu or payload.message_id != menu.get("message_id"):
            return

        mapping = await dm.load_json("reaction_roles", payload.guild_id, {})
        emoji_str = str(payload.emoji)

        if emoji_str in mapping:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(mapping[emoji_str])
            member = guild.get_member(payload.user_id)

            if role and member:
                try:
                    await member.remove_roles(role)
                    logger.info(f"Tog bort roll {role.name} från {member.display_name}")
                except Exception as e:
                    logger.error(f"Kunde inte ta bort roll {role.name}: {e}")

async def setup(bot):
    await bot.add_cog(Roles(bot))
