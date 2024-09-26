import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message contains the specified phrase
        if "Command is on cooldown." in message.content:
            try:
                await message.delete()  # Delete the message
                print(f'Deleted message from {message.author}: {message.content}')
            except discord.Forbidden:
                print("Bot does not have permission to delete messages.")
            except discord.HTTPException as e:
                print(f'Failed to delete message: {e}')

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(Clear(bot))
