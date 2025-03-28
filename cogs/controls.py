import discord
from discord.ext import commands
import random

class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shuffle", help="Mengacak urutan lagu dalam antrian")
    async def shuffle(self, ctx):
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.queue or len(music_cog.queue[guild_id]) < 2:
            await ctx.send("❌ Tidak cukup lagu dalam antrian untuk diacak!")
            return

        random.shuffle(music_cog.queue[guild_id])
        embed = discord.Embed(
            title="🔀 Antrian Lagu Diacak",
            description="Lagu dalam antrian telah diacak!",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="autoplay", help="Mengaktifkan/menonaktifkan autoplay")
    async def autoplay(self, ctx):
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog:
            await ctx.send("❌ Fitur musik tidak tersedia!")
            return

        # Toggle autoplay
        if not hasattr(music_cog, "autoplay_enabled"):
            music_cog.autoplay_enabled = {}

        music_cog.autoplay_enabled[guild_id] = not music_cog.autoplay_enabled.get(guild_id, False)
        status = "✅ **Aktif**" if music_cog.autoplay_enabled[guild_id] else "⛔ **Nonaktif**"

        embed = discord.Embed(
            title="🔄 Autoplay",
            description=f"Autoplay telah diubah menjadi {status}",
            color=discord.Color.green() if music_cog.autoplay_enabled[guild_id] else discord.Color.red(),
        )
        await ctx.send(embed=embed)

# Setup cog
async def setup(bot):
    await bot.add_cog(Controls(bot))
