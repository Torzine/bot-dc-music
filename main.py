import discord
import os
import asyncio
import logging
from discord.ext import commands
from dotenv import load_dotenv

# Load token dari .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


# Logging untuk debugging
logging.basicConfig(level=logging.INFO)

# Intents bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Diperlukan untuk voice

# Inisialisasi bot
bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} siap digunakan!")

async def load_cogs():
    """Memuat semua cogs yang ada di folder /cogs"""
    print("📂 Loading Cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Gagal memuat {filename}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

# Jalankan bot
asyncio.run(main())
