import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from datetime import datetime, timedelta
import aiosqlite

# Define the color
EMBED_COLOR = 0x8c7867
PLACEHOLDER_IMAGE_URL = ""

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = {}
        self.db_ready = False
        bot.loop.create_task(self.initialize_database())

    async def initialize_database(self):
        """Initialize the SQLite database and create the necessary table."""
        self.db = await aiosqlite.connect("daily_data.db")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS daily (
                user_id INTEGER PRIMARY KEY,
                last_claim TEXT
            )
        """)
        await self.db.commit()
        self.db_ready = True

    @commands.command(name='daily')
    async def daily(self, ctx):
        if not self.db_ready:
            await ctx.send("Database is still loading, try again in a moment.")
            return

        user = ctx.author
        now = datetime.utcnow()

        # Check for cooldown
        if user in self.user_cooldowns:
            cooldown_time = self.user_cooldowns[user]
            if now < cooldown_time:
                # User is on cooldown
                time_remaining = discord.utils.format_dt(cooldown_time, 'R')  # Relative timestamp
                embed = self.create_cooldown_embed(user, time_remaining)
                message = await ctx.send(embed=embed)
                view = self.create_embed_view(message)
                await message.edit(view=view)

                # Add hourglass reaction to the original message
                await ctx.message.add_reaction("⏳")

                return

        # Update cooldown in the database
        self.user_cooldowns[user] = now + timedelta(days=1)
        await self.update_user_cooldown(user.id, now.strftime("%Y-%m-%d"))

        next_daily_time = self.user_cooldowns[user]

        # Schedule the task to ping the user in the channel when the cooldown ends
        self.schedule_daily_reminder(ctx, user, next_daily_time)

        # React with checkmark emoji when daily is ready
        await ctx.message.add_reaction("✅")

        # Send embed first, then edit it to add buttons
        message = await ctx.send(embed=self.create_daily_embed(user, next_daily_time))
        view = self.create_embed_view(message)
        await message.edit(view=view)

    def schedule_daily_reminder(self, ctx, user, next_daily_time):
        """Schedule a task to notify the user in the same channel when their daily cooldown ends."""
        delay = (next_daily_time - datetime.utcnow()).total_seconds()
        self.bot.loop.call_later(delay, self.notify_user_in_channel, ctx, user)

    async def notify_user_in_channel(self, ctx, user):
        """Notify the user in the same channel that their daily is ready again."""
        await ctx.send(f"{user.mention}, your `=daily` is ready to claim again!")

    def create_daily_embed(self, user, next_daily_time):
        embed = discord.Embed(
            description=f"{user.mention}, next daily at {discord.utils.format_dt(next_daily_time, 'F')}",
            color=EMBED_COLOR
        )
        embed.set_image(url=PLACEHOLDER_IMAGE_URL)  # Set image below the text
        return embed

    def create_cooldown_embed(self, user, time_remaining):
        embed = discord.Embed(
            description=f"{user.mention}, your daily is on cooldown. Try again {time_remaining}.",
            color=EMBED_COLOR
        )
        embed.set_image(url=PLACEHOLDER_IMAGE_URL)  # Set image below the text
        return embed

    def create_embed_view(self, message):
        view = View()

        # Vote button
        vote_button = Button(label="Vote Cupid", url="https://top.gg/bot/930688392247775313/vote", style=discord.ButtonStyle.link)

        # Clear button
        clear_button = Button(label="Clear", style=discord.ButtonStyle.danger, emoji="🗑️")

        async def clear_embed_callback(interaction):
            await message.delete()
            await interaction.response.send_message("Embed cleared!", ephemeral=True)

        clear_button.callback = clear_embed_callback

        view.add_item(vote_button)
        view.add_item(clear_button)

        return view

    async def update_user_cooldown(self, user_id, last_claim):
        """Update the user's last claim date in the database."""
        await self.db.execute("""
            INSERT INTO daily (user_id, last_claim)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            last_claim = excluded.last_claim
        """, (user_id, last_claim))
        await self.db.commit()

async def setup(bot):
    await bot.add_cog(Daily(bot))
