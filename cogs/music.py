import discord
from discord.ext import commands
import yt_dlp
import asyncio
import re
import os  # Untuk mengambil API Key dari Environment
import aiohttp  # Untuk melakukan request ke YouTube API

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Mengambil API Key dari Environment
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queue = {}
        self.autoplay_enabled = {}

    async def join_voice(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("❌ Kamu harus bergabung ke voice channel dulu!")
            return None

        channel = ctx.author.voice.channel
        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_connected():
            self.voice_clients[ctx.guild.id] = await channel.connect()
        return self.voice_clients[ctx.guild.id]

    @commands.command(name="play", help="Memutar lagu dari YouTube")
    async def play(self, ctx, *, query):
        voice_client = await self.join_voice(ctx)
        if not voice_client:
            return

        url, title = await self.get_youtube_url(query)
        if not url:
            await ctx.send("❌ Lagu tidak ditemukan!")
            return

        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []

        self.queue[ctx.guild.id].append((title, url))

        # Tampilkan antrian otomatis setelah menambahkan lagu
        await self.show_queue(ctx)

        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def get_youtube_url(self, query):
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True"}
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
                    return info["url"], info["title"]
                else:
                    return None, None
            except Exception as e:
                print(f"Error: {e}")
                return None, None

    async def play_next(self, ctx):
        guild_id = ctx.guild.id

        if guild_id in self.queue and self.queue[guild_id]:
            title, url = self.queue[guild_id].pop(0)
            voice_client = self.voice_clients[guild_id]

            FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

            embed = discord.Embed(
                title="🎶 Sekarang Memutar",
                description=f"[{title}]({url})",
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Diputar oleh ZETTA BERNYANYI 🎵")

            await ctx.send(embed=embed)

            def after_play(error):
                if error:
                    print(f"Error: {error}")
                coro = self.play_next(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                fut.result()

            voice_client.play(source, after=after_play)

        elif self.autoplay_enabled.get(guild_id, False):
            autoplay_song = await self.get_autoplay_song(ctx)
            if autoplay_song:
                self.queue[guild_id].append(autoplay_song)
                await self.play_next(ctx)

    async def get_autoplay_song(self, ctx):
        """Menggunakan YouTube API untuk mencari lagu terkait."""
        guild_id = ctx.guild.id
        if not YOUTUBE_API_KEY:
            print("⚠️ API Key YouTube tidak ditemukan!")
            return None

        if guild_id in self.queue and self.queue[guild_id]:
            last_title, _ = self.queue[guild_id][-1]
        else:
            last_title = "music"

        async with aiohttp.ClientSession() as session:
            params = {
                "part": "snippet",
                "maxResults": 1,
                "q": last_title,
                "type": "video",
                "key": YOUTUBE_API_KEY
            }
            async with session.get(YOUTUBE_SEARCH_URL, params=params) as response:
                data = await response.json()
                if "items" in data and data["items"]:
                    video_id = data["items"][0]["id"]["videoId"]
                    title = data["items"][0]["snippet"]["title"]
                    return title, f"https://www.youtube.com/watch?v={video_id}"

        return None

    async def autoplay_next(self, ctx):
    """Memainkan lagu berikutnya berdasarkan rekomendasi (misalnya dari YouTube API)."""
    guild_id = ctx.guild.id

    # Pastikan autoplay diaktifkan dan tidak ada lagu dalam antrian
    if self.autoplay_enabled.get(guild_id, False) and not self.queue.get(guild_id):
        next_song = await self.get_youtube_suggestion()  # Implementasikan fungsi rekomendasi lagu
        if next_song:
            self.queue[guild_id] = [next_song]
            await self.play_next(ctx)


    async def show_queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.queue or not self.queue[guild_id]:
            return

        queue_list = "\n".join([f"{i+1}. {title}" for i, (title, _) in enumerate(self.queue[guild_id])])
        embed = discord.Embed(title="📜 Antrian Lagu", description=queue_list, color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
