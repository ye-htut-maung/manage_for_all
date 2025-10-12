
import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows a list of all available commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Manage for All Bot Help",
            description="Welcome! This bot uses Slash Commands. Just type `/` to see all available commands and their descriptions.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="👥 Member Management",
            value="`/addmember` - Adds a new member.\n"
                  "`/listmembers` - Lists all members.",
            inline=False
        )

        embed.add_field(
            name="📝 Responsibility Management",
            value="`/addresponsibility` - Adds a responsibility to a member.",
            inline=False
        )

        embed.add_field(
            name="🧠 AI Rule Management",
            value="`/viewrules` - Shows the current rules for the AI.\n"
                  "`/addrule` - Adds a new rule for the AI.\n"
                  "`/deleterule` - Deletes a rule by its number.",
            inline=False
        )
        
        embed.add_field(
            name="✅ Task Management",
            value="`/assigntask` - Uses AI to create and assign tasks for an event.\n"
                  "`/tasks` - Views all pending tasks (or tasks for one member).\n"
                  "`/addtask` - Manually adds a new task.\n"
                  "`/completetask` - Marks a task as complete by its ID.",
            inline=False
        )
        
        embed.set_footer(text="Just start typing a command to see its specific options!")

        # Send the embed
        await interaction.response.send_message(embed=embed, ephemeral=False) # change to True if you want only you can see

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))