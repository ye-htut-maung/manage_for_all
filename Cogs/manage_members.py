import discord
from discord.ext import commands
import json
from utils.data_manager import save_members_to_json

class ManageMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send("Hello Buddy! What's up?")

    @commands.command(name='addmember')
    async def add_member(self, ctx, *, content:str):
        # Adds a new member to the board. Format: >addmember Name, Role
        parts = content.split(',')
        if len(parts) == 2:
            name = parts[0].strip()
            role = parts[1].strip()

            member_data = {'name': name, 'role': role, 'responsibilities': []}
            self.bot.members.append(member_data)
            save_members_to_json(self.bot.members)
            await ctx.send(f'✅ Added **{name}** as **{role}**.')
        else:
            await ctx.send("Please use the format: `>addmember Full Name, Role`")
        
    @commands.command(name = 'listmembers')
    async def list_members(self, ctx):
        # list all current board members
        if not self.bot.members:
            await ctx.send("There are no members in the list yet")
            return
        response = "Here are the current board members:\n"
        for member in self.bot.members:
            response += f"- {member['name']}: {member['role']}\n"

        await ctx.send(response)
# load the Cog to the bot
async def setup(bot):
    await bot.add_cog(ManageMembers(bot))