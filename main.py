import discord
import os
import asyncio
import logging
import traceback
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

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} siap digunakan!")

async def load_cogs():
    """Memuat semua cogs secara otomatis dari folder 'cogs'"""
    print("📂 Loading Cogs...")

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"  # Menghapus ".py" dari nama file
            
            try:
                await bot.load_extension(cog_name)
                print(f"✅ Loaded {cog_name}")
            except Exception as e:
                print(f"❌ Gagal memuat {cog_name}: {e}")
                traceback.print_exc()  # Menampilkan error lengkap

    print("📂 Semua Cogs telah dimuat!")

async def main():
    async with bot:
        await load_cogs()  # ✅ Pastikan ini dijalankan sebelum bot start
        print("🚀 Bot akan segera online...")
        await bot.start(TOKEN)

asyncio.run(main())
