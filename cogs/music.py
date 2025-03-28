import discord
from discord.ext import commands
import yt_dlp
import asyncio
import re
import os
import aiohttp

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Mengambil API Key dari Environment Variables

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Menyimpan voice client per server
        self.queue = {}  # Menyimpan antrian lagu tiap server
        self.autoplay_enabled = {}  # Menyimpan status autoplay tiap server
        self.last_video_id = {}  # Menyimpan ID video terakhir yang diputar di tiap server

    async def join_voice(self, ctx):
        """Bergabung ke voice channel pengguna atau kembali jika sudah terhubung."""
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("❌ Kamu harus bergabung ke voice channel dulu!")
            return None

        channel = ctx.author.voice.channel
        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_connected():
            self.voice_clients[ctx.guild.id] = await channel.connect()
        return self.voice_clients[ctx.guild.id]

    @commands.command(name="play", help="Memutar lagu dari YouTube")
    async def play(self, ctx, *, query):
        """Mencari dan memutar lagu berdasarkan URL atau pencarian."""
        voice_client = await self.join_voice(ctx)
        if not voice_client:
            return

        url, title, video_id = await self.get_youtube_url(query)
        if not url:
            await ctx.send("❌ Lagu tidak ditemukan!")
            return

        # Menyimpan lagu ke dalam antrian
        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []
        self.queue[ctx.guild.id].append((title, url, video_id))

        # Jika sedang memutar, tambahkan ke antrian; jika tidak, langsung mainkan
        if voice_client.is_playing():
            embed = discord.Embed(
                title="➕ Lagu Ditambahkan ke Antrian",
                description=f"[{title}]({url})",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"🎶 Total antrian: {len(self.queue[ctx.guild.id])} lagu")
            await ctx.send(embed=embed)
        else:
            await self.play_next(ctx)

    async def get_youtube_url(self, query):
        """Menggunakan yt-dlp untuk mendapatkan URL audio dan judul lagu dari YouTube."""
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        url_pattern = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')
        is_url = re.match(url_pattern, query)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                if is_url:
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    info = info["entries"][0] if info["entries"] else None

                if info:
                    video_id = info["id"]
                    return info["url"], info["title"], video_id
                else:
                    return None, None, None
            except Exception as e:
                print(f"Error: {e}")
                return None, None, None

    async def play_next(self, ctx):
        """Memainkan lagu berikutnya dari antrian atau menggunakan autoplay jika diaktifkan."""
        guild_id = ctx.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            title, url, video_id = self.queue[guild_id].pop(0)
            voice_client = self.voice_clients[guild_id]

            self.last_video_id[guild_id] = video_id  # Simpan ID video terakhir

            FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

            embed = discord.Embed(
                title="🎶 Sekarang Memutar",
                description=f"[{title}]({url})",
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Diputar oleh ZETTA BERNYANYI 🎵")

            await ctx.send(embed=embed)

            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.check_next(ctx), self.bot.loop))
        else:
            await self.autoplay_next(ctx)

    async def check_next(self, ctx):
        """Cek apakah ada lagu berikutnya atau autoplay aktif."""
        guild_id = ctx.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            await self.play_next(ctx)
        elif self.autoplay_enabled.get(guild_id, False):
            await self.autoplay_next(ctx)
        else:
            await self.leave_if_empty(ctx)

    async def leave_if_empty(self, ctx):
        """Keluar dari voice channel jika tidak ada lagu yang tersisa."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and not self.queue.get(guild_id, []):
            await asyncio.sleep(10)  # Tunggu 10 detik sebelum keluar
            if not self.queue.get(guild_id, []) and self.voice_clients[guild_id].is_connected():
                await self.voice_clients[guild_id].disconnect()
                del self.voice_clients[guild_id]
                print("✅ Bot keluar dari voice channel karena antrian kosong.")

    async def autoplay_next(self, ctx):
        """Memainkan lagu berikutnya berdasarkan rekomendasi YouTube."""
        guild_id = ctx.guild.id
        if guild_id in self.last_video_id:
            url, title, video_id = await self.get_recommended_video(self.last_video_id[guild_id])
            if url:
                self.queue.setdefault(guild_id, []).append((title, url, video_id))  
                await self.play_next(ctx)
            else:
                await ctx.send("❌ Tidak dapat menemukan lagu autoplay!")
        else:
            await ctx.send("⚠️ Tidak ada lagu sebelumnya untuk mendapatkan rekomendasi.")

    async def get_recommended_video(self, video_id):
        """Mengambil video rekomendasi dari YouTube API berdasarkan lagu terakhir."""
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={video_id}&type=video&key={YOUTUBE_API_KEY}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if "items" in data and data["items"]:
                    first_result = data["items"][0]
                    video_id = first_result["id"]["videoId"]
                    title = first_result["snippet"]["title"]
                    return f"https://www.youtube.com/watch?v={video_id}", title, video_id
                return None, None, None

async def setup(bot):
    await bot.add_cog(Music(bot))
