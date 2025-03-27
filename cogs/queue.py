import discord
from discord.ext import commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="queue", help="Menampilkan antrian lagu")
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.queue or not music_cog.queue[guild_id]:
            await ctx.send("🎵 Antrian kosong!")
            return

        queue_list = "\n".join([f"{i+1}. {title}" for i, (title, _) in enumerate(music_cog.queue[guild_id])])
        embed = discord.Embed(title="🎶 Antrian Lagu", description=queue_list, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="remove", help="Menghapus lagu dari antrian")
    async def remove(self, ctx, index: int):
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.queue or index < 1 or index > len(music_cog.queue[guild_id]):
            await ctx.send("❌ Indeks tidak valid!")
            return

        removed_song = music_cog.queue[guild_id].pop(index - 1)
        await ctx.send(f"🗑️ Menghapus **{removed_song[0]}** dari antrian!")

    @commands.command(name="move", help="Memindahkan lagu dalam antrian")
    async def move(self, ctx, index: int, new_position: int):
        guild_id = ctx.guild.id
        music_cog = self.bot.get_cog("Music")

        if not music_cog or guild_id not in music_cog.queue or index < 1 or index > len(music_cog.queue[guild_id]) or new_position < 1 or new_position > len(music_cog.queue[guild_id]):
            await ctx.send("❌ Indeks tidak valid!")
            return

        song = music_cog.queue[guild_id].pop(index - 1)
        music_cog.queue[guild_id].insert(new_position - 1, song)
        await ctx.send(f"🔀 Memindahkan **{song[0]}** ke posisi {new_position}!")

# Setup cog
async def setup(bot):
    await bot.add_cog(Queue(bot)) 