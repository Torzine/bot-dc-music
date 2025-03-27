import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Menyimpan voice client untuk tiap server (guild)
        self.queue = {}  # Menyimpan antrian lagu tiap server
    
    async def join_voice(self, ctx):
        """Join ke voice channel pengguna"""
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("❌ Kamu harus bergabung ke voice channel dulu!")
            return None
        channel = ctx.author.voice.channel
        if ctx.guild.id not in self.voice_clients:
            self.voice_clients[ctx.guild.id] = await channel.connect()
        return self.voice_clients[ctx.guild.id]

    def get_youtube_url(self, query):
        """Mencari video YouTube berdasarkan query"""
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if "entries" in info and len(info["entries"]) > 0:
                    return info["entries"][0]["url"], info["entries"][0]["title"]
                else:
                    return None, None
            except Exception as e:
                print(f"Error: {e}")
                return None, None

    @commands.command(name="play", help="Memutar lagu dari YouTube")
    async def play(self, ctx, *, query):
        """Command untuk memutar lagu"""
        await ctx.send(f"🔍 Mencari lagu: `{query}`...")
        
        url, title = self.get_youtube_url(query)
        if not url:
            await ctx.send("❌ Tidak bisa menemukan lagu yang sesuai.")
            return

        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []
        
        self.queue[ctx.guild.id].append((title, url))
        
        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        """Memutar lagu berikutnya di antrian"""
        guild_id = ctx.guild.id
        if guild_id in self.queue and self.queue[guild_id]:
            title, url = self.queue[guild_id].pop(0)
            voice_client = await self.join_voice(ctx)

            FFMPEG_OPTIONS = {"options": "-vn"}
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

            await ctx.send(f"🎶 Sekarang memutar: **{title}**")

    @commands.command(name="skip", help="Melewati lagu saat ini")
    async def skip(self, ctx):
        """Melewati lagu saat ini dan memutar lagu berikutnya"""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            await ctx.send("⏭️ Lagu dilewati!")
            await self.play_next(ctx)

    @commands.command(name="pause", help="Pause lagu")
    async def pause(self, ctx):
        """Menjeda lagu yang sedang diputar"""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].pause()
            await ctx.send("⏸️ Lagu dijeda!")

    @commands.command(name="resume", help="Lanjutkan lagu")
    async def resume(self, ctx):
        """Melanjutkan lagu yang dijeda"""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_paused():
            self.voice_clients[guild_id].resume()
            await ctx.send("▶️ Lagu dilanjutkan!")

    @commands.command(name="leave", help="Keluar dari voice channel")
    async def leave(self, ctx):
        """Bot keluar dari voice channel"""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients:
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
            await ctx.send("👋 Keluar dari voice channel!")

async def setup(bot):
    await bot.add_cog(Music(bot))