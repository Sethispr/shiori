import discord
from discord.ext import commands

# Define bot and intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='=', intents=intents)

# Load cogs from the cogs folder
@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    
    # Load cogs
    await bot.load_extension('cogs.hourly')
    await bot.load_extension('cogs.daily')
    await bot.load_extension('cogs.ping')
    await bot.load_extension('cogs.raid_cog')

bot.run("DISCORD_BOT_TOKEN")
