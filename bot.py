import discord
import os
from dotenv import load_dotenv
import json
from google import genai
from discord.ext import commands
import asyncpg


# ----- SETUP -----
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_PW = os.getenv('DB_PW')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
allowed_ids_str = os.getenv('ALLOWED_CHANNEL_IDS')
if allowed_ids_str:
    ALLOWED_CHANNEL_IDS = [int(id_str) for id_str in allowed_ids_str.split(',')]
else:
    ALLOWED_CHANNEL_IDS = []
    print("WARNING: ALLOWED_CHANNEL_IDS was not found in the .env file.")


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.db_pool = None
        super().__init__(command_prefix='>', intents=intents)

    async def setup_hook(self):
        # This runs once after the bot logs in but before it's fully connected.

        # ----- DATABASE CONNECTION -----
        try:
            self.db_pool = await asyncpg.create_pool(
                database=DB_NAME, user=DB_USER, password=DB_PW
            )
            print("Successfully connected to the PostgreSQL database.")
        except Exception as e:
            print(f"Error: Could not connect to the database. {e}")

        # ----- COG LOADING -----
        for filename in os.listdir('./Cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'Cogs.{filename[:-3]}')
                print(f'Loaded Cog: {filename}')

        # ----- COMMAND SYNCING -----
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)


bot = MyBot()

# @bot.check
# async def restrict_to_allowed_channels(ctx):
#     return ctx.channel.id in ALLOWED_CHANNEL_IDS

bot.run(TOKEN)






