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
bot = commands.Bot(command_prefix="!", intents=intents)

# Memuat semua cogs
COGS = ["cogs.music", "cogs.controls", "cogs.queue", "cogs.events"]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} telah online!")

async def load_cogs():
    for cog in COGS:
        await bot.load_extension(cog)
        print(f"🔄 Loaded: {cog}")

# Menjalankan bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
