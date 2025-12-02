# ==================== UTILS_CORE.PY ====================
import asyncio, json, logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

import discord
from discord.ext import commands
from discord import app_commands

# === Logger setup ===
logger = logging.getLogger(__name__)
temp_logger = logging.getLogger("temp_messages")
temp_handler = logging.FileHandler("logs/temp_messages.log", encoding="utf-8")
temp_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
temp_logger.addHandler(temp_handler)
temp_logger.setLevel(logging.INFO)

# === Paths ===
DATA_DIR = Path("data")
CONFIG_FILE = Path("config.json")

# === Dataclass för användarstatistik ===
@dataclass
class UserStats:
    messages: int = 0
    xp: int = 0
    level: int = 1
    total_xp: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

# === DataManager för JSON och config ===
class DataManager:
    def __init__(self):
        self.locks: Dict[str, asyncio.Lock] = {}
        self.config: dict = self._load_config()
        self.config_lock = asyncio.Lock()

    def _get_lock(self, key: str) -> asyncio.Lock:
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        return self.locks[key]

    def _load_config(self) -> dict:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Kunde inte ladda config: {e}")
        return {
            "xp": {"per_message": 5, "per_pending": 2, "base_xp": 100},
            "timeouts": {"default": 60, "quotes": 600},
            "limits": {"dice_amount": 50, "dice_sides": 1000, "import_limit": 5000}
        }

    async def reload_config(self) -> dict:
        async with self.config_lock:
            self.config = self._load_config()
            logger.info("🌐 Config reloaded")
            return self.config

    def get_timeout(self, key: str = "default") -> int:
        return self.config.get("timeouts", {}).get(key, 60)

    async def load_json(self, filename: str, guild_id: int, default: Any = None) -> Any:
        file = DATA_DIR / f"{filename}_{guild_id}.json"
        try:
            async with self._get_lock(str(file)):
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except FileNotFoundError:
            return default if default is not None else {}
        except json.JSONDecodeError:
            logger.warning(f"Korrupt JSON i {file}, använder default")
            return default if default is not None else {}
        except Exception as e:
            logger.error(f"Fel vid läsning av {file}: {e}")
            return default if default is not None else {}

    async def save_json(self, filename: str, guild_id: int, data: dict) -> bool:
        file = DATA_DIR / f"{filename}_{guild_id}.json"
        try:
            async with self._get_lock(str(file)):
                DATA_DIR.mkdir(exist_ok=True)
                await asyncio.to_thread(lambda: json.dump(data, open(file, "w", encoding="utf-8"), indent=2))
                return True
        except Exception as e:
            logger.error(f"Fel vid sparande till {file}: {e}")
            return False

dm = DataManager()

# === Tillfälligt meddelande med AI‑flagga och config‑styrd timeout ===
async def send_temp(target, content: Optional[str] = None, embed: Optional[discord.Embed] = None, timeout_key: str = "default", is_ai: bool = False):
    """
    Skickar ett meddelande som raderas efter delay från config.json (via timeout_key), om is_ai=False.
    Fungerar för både ctx.send() och interaction.response/followup.send().
    Loggar alla skickade meddelanden.
    """
    try:
        if is_ai:
            temp_logger.info(f"[AI] Skickade permanent meddelande: {content or embed.title}")
            return await target.send(content=content, embed=embed)

        delay = dm.get_timeout(timeout_key)
        msg = await target.send(content=content, embed=embed)
        temp_logger.info(f"[TEMP] Skickade meddelande som raderas om {delay}s: {content or embed.title}")
        await asyncio.sleep(delay)
        await msg.delete()
        temp_logger.info(f"[TEMP] Raderade meddelande: {content or embed.title}")
    except Exception as e:
        temp_logger.warning(f"Fel i send_temp: {e}")

# === Slash-kommando för att ladda om config ===
class UtilsCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="reloadconfig",
        description="Ladda om config.json",
        extras={"cog": "System", "help_text": "Laddar om inställningar från config.json utan att starta om botten."}
    )
    @app_commands.default_permissions(administrator=True)
    async def reload_config(self, interaction: discord.Interaction):
        await dm.reload_config()
        embed = discord.Embed(
            title="🔄 Config omladdad",
            description="Nya inställningar gäller direkt.",
            color=0x00ff99
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# === Hjälpembed-generator ===
def generate_help_embed(commands: list, is_admin: bool) -> discord.Embed:
    grouped: Dict[str, list] = {}
    for cmd in commands:
        if cmd.default_permissions and not is_admin:
            continue
        cog_name = cmd.extras.get("cog", "Övrigt")
        grouped.setdefault(cog_name, []).append(cmd)

    embed = discord.Embed(
        title="🧪 Puffin Tech Support – Kommandon",
        description="Här är alla kommandon:",
        color=0x0099ff
    )

    for category, cmds in grouped.items():
        lines = [f"`/{cmd.name}` – {cmd.description}" for cmd in cmds]
        embed.add_field(name=f"📂 {category}", value="\n".join(lines), inline=False)

    return embed

# === Setup ===
async def setup(bot):
    await bot.add_cog(UtilsCore(bot))
