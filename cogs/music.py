import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Menyimpan voice client tiap server
        self.queue = {}  # Menyimpan antrian lagu tiap server

    async def join_voice(self, ctx):
        """Bergabung ke voice channel pengguna atau kembali jika terputus."""
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("❌ Kamu harus bergabung ke voice channel dulu!")
            return None

        channel = ctx.author.voice.channel
        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_connected():
            self.voice_clients[ctx.guild.id] = await channel.connect()
        return self.voice_clients[ctx.guild.id]

    @commands.command(name="play", help="Memutar lagu dari YouTube")
    async def play(self, ctx, *, query):
        """Memainkan lagu berdasarkan URL atau pencarian."""
        voice_client = await self.join_voice(ctx)
        if not voice_client:
            return

        url = await self.get_youtube_url(query)
        if not url:
            await ctx.send("❌ Lagu tidak ditemukan!")
            return

        FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []

        self.queue[ctx.guild.id].append((query, url))

        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def get_youtube_url(self, query):
        """Menggunakan yt-dlp untuk mendapatkan URL audio."""
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                return info["entries"][0]["url"] if info["entries"] else None
            except Exception as e:
                print(f"Error: {e}")
                return None

    async def play_next(self, ctx):
        """Memainkan lagu berikutnya di antrian."""
        guild_id = ctx.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            title, url = self.queue[guild_id].pop(0)
            voice_client = self.voice_clients[guild_id]

            FFMPEG_OPTIONS = {"options": "-vn"}
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

            await ctx.send(f"🎶 Sekarang memutar: **{title}**")

    @commands.command(name="stop", help="Menghentikan lagu dan mengosongkan antrian")
    async def stop(self, ctx):
        """Menghentikan lagu dan mengosongkan antrian."""
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].stop()
            self.queue[ctx.guild.id] = []  # Kosongkan antrian
            await ctx.send("⏹️ Pemutaran dihentikan dan antrian dikosongkan.")

    @commands.command(name="leave", help="Bot keluar dari voice channel")
    async def leave(self, ctx):
        """Bot keluar dari voice channel dan menghapus data voice client."""
        if ctx.guild.id in self.voice_clients:
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]  # Hapus data voice client
            self.queue.pop(ctx.guild.id, None)  # Hapus antrian jika ada
            await ctx.send("👋 Bot telah keluar dari voice channel.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Auto-reconnect jika bot terputus dari voice channel."""
        if member == self.bot.user:
            if before.channel is not None and after.channel is None:
                guild_id = before.channel.guild.id
                if guild_id in self.voice_clients:
                    del self.voice_clients[guild_id]  # Hapus data jika bot keluar paksa
                    print(f"⚠️ Bot dikeluarkan dari voice channel di {member.guild.name}")

async def setup(bot):
    await bot.add_cog(Music(bot))
