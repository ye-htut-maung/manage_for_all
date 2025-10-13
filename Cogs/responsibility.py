# Cogs/responsibility.py
import discord
from discord.ext import commands
import json
from utils.data_manager import add_responsibility_to_db, delete_responsibility_from_db, get_all_responsibilities_with_member
from discord import app_commands

class Responsibility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

   
    @app_commands.command(name="addresponsibility", description="Add a responsibility to a member")
    @app_commands.describe(name="The full name of the member", responsibility="The responsibility that a member is given")
    async def add_responsibility(self, interaction: discord.Interaction, name: str, responsibility:str):

        result = await add_responsibility_to_db(self.bot.db_pool, name, responsibility)

        if result == "success":
            await interaction.response.send_message(f"✅ Added a new responsibility to **{name}**.")
        elif result == "member_not_found":
            await interaction.response.send_message(f'❌ Error: Member "{name}" was not found.', ephemeral=True)
        else:
            await interaction.response.send_message("❌ An error occurred while adding the responsibility.", ephemeral=True)
    
    @app_commands.command(name="deleteresponsibility", description="Deletes a responsibility by its ID.")
    @app_commands.describe(responsibility_id="The ID number of the responsibility to delete (use /viewmember to find it).")
    async def delete_responsibility(self, interaction: discord.Interaction, responsibility_id: int):
        deleted_text = await delete_responsibility_from_db(self.bot.db_pool, responsibility_id)

        if deleted_text:
            await interaction.response.send_message(f'🗑️ Deleted responsibility #{responsibility_id}: "{deleted_text}"')
        else:
            await interaction.response.send_message(f"❌ Error: Responsibility with ID #{responsibility_id} was not found.", ephemeral=True)


    @app_commands.command(name="viewresponsibilities", description="Shows a list of all assigned responsibilities.")
    async def view_responsibilities(self, interaction: discord.Interaction):
        responsibilities = await get_all_responsibilities_with_member(self.bot.db_pool)
        
        if not responsibilities:
            await interaction.response.send_message("There are no responsibilities assigned to any members yet.")
            return

        embed = discord.Embed(
            title="📝 All Assigned Responsibilities",
            color=discord.Color.orange()
        )

        member_responsibilities = {}
        for r in responsibilities:
            member_name = r['member_name']
            if member_name not in member_responsibilities:
                member_responsibilities[member_name] = []
            member_responsibilities[member_name].append(f"- **ID #{r['id']}:** {r['responsibility_text']}")

        for member_name, resp_list in member_responsibilities.items():
            embed.add_field(
                name=f"👤 {member_name}",
                value="\n".join(resp_list),
                inline=False
            )

        await interaction.response.send_message(embed=embed)
    

# load the Cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Responsibility(bot))