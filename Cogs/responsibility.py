# Cogs/responsibility.py
import discord
from discord.ext import commands
import json
from utils.data_manager import save_members_to_json
from discord import app_commands

class Responsibility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

   
    @app_commands.command(name="addresponsibility", description="Add a responsibility to a member")
    @app_commands.describe(name="The full name of the member", responsibility="The responsibility that a member is given")
    async def add_responsibility(self, interaction: discord.Interaction, name: str, responsibility:str):
        found = False
        # search member
        # TODO: update search runtime
        for member in self.bot.members:
            if member["name"].lower() == name.lower():
                member["responsibilities"].append(responsibility)
                found = True
                break
        if not found:
            await interaction.response.send_message(f'Error: Member "{name}" was not found. Please check the spelling or check the list members')
            return

        save_members_to_json(self.bot.members)

        await interaction.response.send_message(f"✅ Added a new responsibility to **{name}**.")
        # for debug
        print(f"Current members: {self.bot.members}")
        

# load the Cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Responsibility(bot))