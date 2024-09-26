import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime, timedelta
import aiosqlite
import asyncio

# Define the color
EMBED_COLOR = 0xfff271
PLACEHOLDER_IMAGE_URL = ""

class Hourly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = {}
        self.db_ready = False
        bot.loop.create_task(self.initialize_database())

    async def initialize_database(self):
        """Initialize the SQLite database and create the necessary table."""
        self.db = await aiosqlite.connect("hourly_streaks.db")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                user_id INTEGER PRIMARY KEY,
                streak INTEGER DEFAULT 0,
                last_claim TEXT
            )
        """)
        await self.db.commit()
        self.db_ready = True

    @commands.command(name='hourly')
    async def hourly(self, ctx):
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
                time_remaining = cooldown_time - now
                minutes_remaining = int(time_remaining.total_seconds() // 60)
                embed = self.create_cooldown_embed(user, minutes_remaining)
                message = await ctx.send(embed=embed)
                view = self.create_embed_view(message)
                await message.edit(view=view)

                # Add hourglass reaction to the original message
                await ctx.message.add_reaction("<:hourglass_darkmode:1288303642558074882>")
                return

        # Fetch streak data from the database
        streak, last_claim = await self.get_user_streak(user.id)

        # If the last claim was not today, reset streak
        last_claim_date = datetime.strptime(last_claim, "%Y-%m-%d") if last_claim else None
        if last_claim_date and last_claim_date.date() != now.date():
            streak = 0

        # Increment streak
        streak += 1

        # Update cooldown and streak in database
        self.user_cooldowns[user] = now + timedelta(hours=1)
        await self.update_user_streak(user.id, streak, now.strftime("%Y-%m-%d"))

        # React with checkmark emoji when hourly is ready
        await ctx.message.add_reaction("<:tick_darkmode:1288304495549480970>")

        # Calculate remaining time until the next hourly claim
        next_hourly_time = self.user_cooldowns[user]
        remaining_time = next_hourly_time - now
        minutes_remaining = int(remaining_time.total_seconds() // 60)

        # Send embed with the next hourly time and remaining time
        message = await ctx.send(embed=self.create_hourly_embed(user, streak, minutes_remaining))
        view = self.create_embed_view(message)
        await message.edit(view=view)

        # Schedule the task to notify the user when their cooldown ends
        self.schedule_hourly_reminder(ctx.channel, user)

    def schedule_hourly_reminder(self, channel, user):
        # Schedule a task to notify the user when their cooldown ends
        next_hourly_time = self.user_cooldowns[user]
        delay = (next_hourly_time - datetime.utcnow()).total_seconds()

        # Instead of using call_later, use asyncio.create_task to handle the coroutine properly
        asyncio.create_task(self.delayed_reminder(delay, channel, user))

    async def delayed_reminder(self, delay, channel, user):
        # Wait for the cooldown to expire before sending the reminder
        await asyncio.sleep(delay)
        await self.send_reminder(channel, user)

    async def send_reminder(self, channel, user):
        # Notify the user that their hourly is ready
        await channel.send(f"""<:notification_darkmode:1288305377619738739>{user.mention}, your `=hourly` is ready to claim again!\n```ansi
[2;40m[2;33m=hourly[0m[2;40m[0m
```""")

    def create_hourly_embed(self, user, streak, minutes_remaining):
        embed = discord.Embed(
            description=f"<:alarm_on_darkmode:1288301874163880006> {user.mention}, you have claimed your hourly!\nStreak: {streak} <:streak_darkmode:1288305822153310261>",
            color=EMBED_COLOR
        )
        embed.set_image(url=PLACEHOLDER_IMAGE_URL)  # Set image below the text
        return embed

    def create_cooldown_embed(self, user, minutes_remaining):
        embed = discord.Embed(
            description=f"<:hourglass_darkmode:1288303642558074882> {user.mention}, your hourly is on cooldown. Try again in **`{minutes_remaining}`** minutes.",
            color=EMBED_COLOR
        )
        embed.set_image(url=PLACEHOLDER_IMAGE_URL)  # Set image below the text
        return embed

    def create_embed_view(self, message):
        view = View()

        # Vote button
        vote_button = Button(label="Vote Cupid", url="https://top.gg/bot/930688392247775313/vote", style=discord.ButtonStyle.link)

        # Clear button
        clear_button = Button(label="Clear", style=discord.ButtonStyle.danger, emoji="<:remove_darkmode:1288304999964872795>")

        async def clear_embed_callback(interaction):
            if message:
                await message.delete()
            await interaction.response.send_message("", ephemeral=True)

        clear_button.callback = clear_embed_callback

        view.add_item(vote_button)
        view.add_item(clear_button)

        return view

    async def get_user_streak(self, user_id):
        """Fetch the user's streak and last claim date."""
        async with self.db.execute("SELECT streak, last_claim FROM streaks WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return result
            return 0, None

    async def update_user_streak(self, user_id, streak, last_claim):
        """Update the user's streak and last claim date."""
        await self.db.execute("""
            INSERT INTO streaks (user_id, streak, last_claim)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            streak = excluded.streak,
            last_claim = excluded.last_claim
        """, (user_id, streak, last_claim))
        await self.db.commit()

async def setup(bot):
    await bot.add_cog(Hourly(bot))
