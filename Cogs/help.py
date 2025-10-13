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
            description="This bot helps manage the club's board members, responsibilities, and tasks using Slash Commands. Just type `/` to see a list.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Start typing any command to see its specific options and descriptions.")

        embed.add_field(
            name="👥 Member Management",
            value="`/addmember` - Add a new member.\n"
                  "`/editmember` - Edit a member's name or role.\n"
                  "`/deletemember` - Delete a member.\n"
                  "`/listmembers` - View a simple list of all members.\n"
                  "`/viewmember` - See a detailed profile for one member.",
            inline=False
        )

        embed.add_field(
            name="📝 Responsibility & Rule Management",
            value="`/addresponsibility` - Add a responsibility to a member.\n"
                  "`/deleteresponsibility` - Delete a responsibility by its ID.\n"
                  "`/viewresponsibilities` - See a list of all responsibilities.\n"
                  "`/addrule` - Add a new rule for the AI.\n"
                  "`/deleterule` - Delete an AI rule by its ID.\n"
                  "`/viewrules` - See all current AI rules.",
            inline=False
        )
        
        embed.add_field(
            name="✅ Task Management",
            value="`/assigntask` - (AI) Create and assign tasks for an event.\n"
                  "`/addtask` - Manually add a new task.\n"
                  "`/tasks` - View all pending tasks.\n"
                  "`/completetask` - Mark a task as complete by its ID.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))