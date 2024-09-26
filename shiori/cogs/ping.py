import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds

        # Create an embed for the ping response
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"Latency is {latency}ms",
            color=0x8c7867
        )

        # Send the embed without any buttons
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
