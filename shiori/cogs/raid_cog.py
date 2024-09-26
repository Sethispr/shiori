import discord
from discord.ext import commands
import re
import asyncio  

class RaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message contains the cooldown phrase and delete it
        if "Command is on cooldown." in message.content:
            await message.delete()
            return  # Exit early after deleting the message
        
        # Check for stamina reward message THIS IS SUPPOSED TO BE IN HOURLY COG
        stamina_reward_pattern = re.compile(r'Hourly Reward recived, (\d+) Stamina !', re.IGNORECASE)
        stamina_match = stamina_reward_pattern.search(message.content)
        
        if stamina_match:
            stamina_amount = stamina_match.group(1)
            embed_message = discord.Embed(
                description=f"You have claimed **{stamina_amount} Stamina**! 🎉",
                color=discord.Color.from_str("#4caf50")  # Green color for success
            )
            await message.channel.send(embed=embed_message)

        # Define the target raid names you're interested in
        target_raids = {
            "Orihime", "Sylvia", "Feitan", "Killua", "Inosuke", 
            "Roronoa", "Kallen", "Levi", "Kokushibo", "Juuzou", 
            "Gowther", "Trunks", "Senku", "Shion", "Suzaku", 
            "Violet", "Izuku", "Neji", "Misteln", "Aqua", 
            "Yamada Asaemon", "Sanji", "Tsukasa"
        }

        if message.embeds:
            embed = message.embeds[0]

            # Extract content from embed fields
            fields_content = self.extract_fields(embed)

            # Clean the content
            clean_content = self.clean_content(fields_content)

            # Process the cleaned content to extract relevant details
            extracted_details = self.process_raid_data(clean_content)

            # Send each extracted detail only if it matches the target raids
            if extracted_details:
                messages = []  # Store references to the sent messages
                for details in extracted_details:
                    # Check if any target name is in the raid name
                    if any(target_name.lower() in details['name'].lower() for target_name in target_raids):
                        embed_message = discord.Embed(
                            description=( 
                                f"**{details['name']}**\n"
                                f"{details['players']} Players, {details['time_left']} left\n"
                                f"{details['rarity']} | Mat: {details['maturation']} | Lvl: {details['level']}\n"
                                f"""```ansi
[2;40m[2;33m=rd join {details['raid_id']}[0m[2;40m[0m
```"""
                            ),
                            color=discord.Color.from_str("#fff271")
                        )
                        message_sent = await message.channel.send(embed=embed_message)
                        messages.append(message_sent)  # Append the sent message to the list
                        await asyncio.sleep(1)  # Add a 1-second delay between messages to avoid rate limits

                # Wait for 10 seconds before deleting messages
                await asyncio.sleep(10)

                # Delete each sent message with a slight delay to avoid rate limits
                for msg in messages:
                    await msg.delete()
                    await asyncio.sleep(1)  # Delay of 1 second between deletions

    def extract_fields(self, embed):
        fields_content = []
        for field in embed.fields:
            fields_content.append(f"{field.name} | {field.value}")  # Combine name and value
        return "\n".join(fields_content)

    def clean_content(self, content):
        # Remove the specific unwanted symbol '㊀' and ensure single spacing
        content = content.replace('㊀', '')  # Remove the '㊀' symbol
        content = re.sub(r'\s+', ' ', content)  # Ensure all content is single-spaced
        content = re.sub(r'[^\w\s\|]', '', content)  # Remove other unwanted special characters, keeping spaces and words
        content = content.replace('|', ' ')  # Replace '|' with a single space for readability
        return content.strip()  # Remove leading/trailing spaces

    def process_raid_data(self, data):
        extracted_details = []

        # Improved regex to capture all variations of raid entries
        raid_pattern = re.compile(
            r'(\d+)\s+(.+?)\s+Players\s+(\d+)\s+Rarity\s+([A-Za-z\s]+)\s+Maturation\s+(\d+)\s+Lvl\s+(\d+)\s+Raid Id\s+(\d+)\s+Time Left\s+(\d+\s+Mins)',
            re.MULTILINE | re.DOTALL
        )
        matches = raid_pattern.findall(data)

        for match in matches:
            # Extracted values
            raid_details = {
                'raid_number': match[0],
                'name': match[1],
                'players': match[2],
                'rarity': match[3],
                'maturation': match[4],
                'level': match[5],
                'raid_id': match[6],
                'time_left': match[7]
            }

            extracted_details.append(raid_details)

        return extracted_details

async def setup(bot):
    await bot.add_cog(RaidCog(bot))
