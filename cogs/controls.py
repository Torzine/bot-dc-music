import discord
from discord.ext import commands
import random
import asyncio

class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shuffle", help="Mengacak urutan lagu dalam antrian")
    async def shuffle(self, ctx):
        """Mengacak lagu dalam antrian."""
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.queue or len(music_cog.queue[guild_id]) < 2:
            await ctx.send("❌ Tidak cukup lagu dalam antrian untuk diacak!")
            return

        random.shuffle(music_cog.queue[guild_id])
        await ctx.send("🔀 Lagu dalam antrian telah diacak!")

    @commands.command(name="autoplay", help="Mengaktifkan/menonaktifkan autoplay")
    async def autoplay(self, ctx):
        """Mengaktifkan atau menonaktifkan autoplay di server."""
        music_cog = self.bot.get_cog("Music")
        guild_id = ctx.guild.id

        if not music_cog:
            await ctx.send("⚠️ Musik belum diinisialisasi.")
            return

        # Toggle autoplay
        music_cog.autoplay_enabled[guild_id] = not music_cog.autoplay_enabled.get(guild_id, False)
        status = "Aktif ✅" if music_cog.autoplay_enabled[guild_id] else "Nonaktif ⛔"
        await ctx.send(f"🔄 Autoplay: **{status}**")

    @commands.command(name="skip", help="Melewati lagu saat ini")
    async def skip(self, ctx):
        """Melewati lagu saat ini dan memainkan lagu berikutnya."""
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.voice_clients:
            await ctx.send("❌ Bot tidak terhubung ke voice channel!")
            return

        voice_client = music_cog.voice_clients[guild_id]

        if not voice_client.is_playing():
            await ctx.send("❌ Tidak ada lagu yang sedang diputar.")
            return

        await ctx.send("⏭️ Melewati lagu...")
        voice_client.stop()  # Menghentikan lagu saat ini

        # Panggil fungsi untuk memainkan lagu berikutnya
        await music_cog.check_next(ctx)

    @commands.command(name="check_api", help="Cek apakah API YouTube aktif dan bisa memberikan rekomendasi lagu")
    async def check_api(self, ctx):
        """Cek apakah API YouTube bisa memberikan rekomendasi lagu."""
        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            await ctx.send("⚠️ Musik belum diinisialisasi.")
            return

        guild_id = ctx.guild.id
        if guild_id not in music_cog.last_video_id:
            await ctx.send("⚠️ Tidak ada lagu terakhir untuk mendapatkan rekomendasi.")
            return

        video_id = music_cog.last_video_id[guild_id]
        url, title, new_video_id = await music_cog.get_recommended_video(video_id)

        if url:
            embed = discord.Embed(
                title="✅ API YouTube Berfungsi",
                description=f"🎶 Rekomendasi lagu ditemukan:\n**[{title}]({url})**",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ API YouTube tidak dapat memberikan rekomendasi lagu!")

async def setup(bot):
    await bot.add_cog(Controls(bot))
