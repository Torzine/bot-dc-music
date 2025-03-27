import discord
from discord.ext import commands
import json
import os
import datetime

LOG_FILE = "log.json"

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_log_file()

    def ensure_log_file(self):
        """Membuat file log jika belum ada"""
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)

    def log_event(self, event_type, details):
        """Menyimpan log ke dalam log.json"""
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

        logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": event_type,
            "details": details
        })

        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        """Event ketika bot siap digunakan"""
        print(f"✅ {self.bot.user} berhasil online!")
        self.log_event("BOT_READY", {"status": "online"})

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Menangani error dalam command"""
        error_message = str(error)
        await ctx.send(f"❌ Terjadi kesalahan: `{error_message}`")
        self.log_event("ERROR", {"command": ctx.command.name if ctx.command else "Unknown", "error": error_message})

# Setup cog
async def setup(bot):
    await bot.add_cog(Events(bot)) 