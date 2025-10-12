import discord
from discord.ext import commands
from discord import app_commands
import json
from utils.data_manager import save_members_to_json

class ManageMembers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="hello", description="Say Hello to test if the bot is working")
    async def hello(self, interaction:discord.Interaction):
        await interaction.response.send_message("Hello Buddy! What's up?")

    @app_commands.command(name='addmember', description="Adds a new member to the board.")
    @app_commands.describe(name="The full name of the member", role = "The member's board position")
    async def add_member(self, interaction: discord.Interaction, name:str, role:str):
        # Adds a new member to the board. Format: >addmember Name, Role

        member_data = {'name': name, 'role': role, 'responsibilities': []}
        self.bot.members.append(member_data)
        save_members_to_json(self.bot.members)
        await interaction.response.send_message(f'✅ Added **{name}** as **{role}**.')

        
        
    @app_commands.command(name = 'listmembers', description="Lists all current board members.")
    async def list_members(self, interaction: discord.Interaction):
        # list all current board members
        if not self.bot.members:
            await interaction.response.send_message("There are no members in the list yet")
            return
        response = "Here are the current board members:\n"
        for member in self.bot.members:
            response += f"- {member['name']}: {member['role']}\n"

        await interaction.response.send_message(response)
# load the Cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ManageMembers(bot))