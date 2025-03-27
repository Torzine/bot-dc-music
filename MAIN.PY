import discord
from discord.ext import commands
import os
import traceback
from config import TOKEN, PREFIX
import asyncio
# Inisialisasi bot dengan intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Event ketika bot siap digunakan
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} siap digunakan!")

# Fungsi untuk memuat semua cogs
async def load_cogs():
    print("📂 Loading Cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"❌ Gagal memuat {filename}: {e}")
                traceback.print_exc()
    print("📂 Semua Cogs telah dimuat!")

# Menjalankan bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


asyncio.run(main())
