# Cogs/responsibility.py
import discord
from discord.ext import commands
import json
from utils.data_manager import save_members_to_json

class Responsibility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # >addresponsibility full name, responsibility
    @commands.command(name="addresponsibility")
    async def add_responsibility(self, ctx, *, content:str):
        parts = content.split(',')
        if len(parts) == 2:
            name = parts[0].strip()
            responsibility = parts[1].strip()
            found = False
            # search member
            # TODO: update search runtime
            for member in self.bot.members:
                if member["name"] == name:
                    member["responsibilities"].append(responsibility)
                    found = True
            if not found:
                await ctx.send(f'The member is not added')
                return

            save_members_to_json(self.bot.members)

            await ctx.send(f'Added **{name}**\'s responsibility as **{responsibility}**')
            # for debug
            print(f"Current members: {self.bot.members}")
        else:
            await ctx.send("Please use the format: `>addresponsibility Full Name, Responsibility`")

# load the Cog to the bot
async def setup(bot):
    await bot.add_cog(Responsibility(bot))