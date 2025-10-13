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
DB_HOST = os.getenv('DB_HOST')


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
                host = DB_HOST,
                database=DB_NAME, 
                user=DB_USER, 
                password=DB_PW
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

bot.run(TOKEN)






