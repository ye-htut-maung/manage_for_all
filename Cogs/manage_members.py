import discord
from discord.ext import commands
from discord import app_commands
import json
from utils.data_manager import add_member_to_db, delete_member_from_db, get_simple_member_list, edit_member_in_db, get_full_member_details


class ManageMembers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="hello", description="Say Hello to test if the bot is working")
    async def hello(self, interaction:discord.Interaction):
        await interaction.response.send_message("Hello Buddy! What's up?")

    @app_commands.command(name='addmember', description="Adds a new member to the board.")
    @app_commands.describe(name="The full name of the member", role = "The member's board position")
    async def add_member(self, interaction: discord.Interaction, name:str, role:str):

        success = await add_member_to_db(self.bot.db_pool, name, role)
        if success:
            await interaction.response.send_message(f'✅ Added **{name}** as **{role}** to the database.')
        else:
            await interaction.response.send_message('❌ An error occurred while adding the member.', ephemeral=True)

        
        
    @app_commands.command(name = 'listmembers', description="Lists all current board members.")
    async def list_members(self, interaction: discord.Interaction):
        # list all current board members
        member_records = await get_simple_member_list(self.bot.db_pool)
        if not member_records:
            await interaction.response.send_message("There are no members in the list yet")
            return
        embed = discord.Embed(
            title="👥 Board Members",
            description="Here is the current list of all board members.",
            color=discord.Color.blue()
        )
        for member in member_records:
            embed.add_field(name=member['name'], value=f"**Role:** {member['role']}", inline=False)
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="deletemember", description="Deletes a member from the board.")
    @app_commands.describe(name="The full name of the member to delete.")
    async def delete_member(self, interaction: discord.Interaction, name: str):
        deleted_member_name = await delete_member_from_db(self.bot.db_pool, name)
        # If a member was found, remove them
        if deleted_member_name:
            await interaction.response.send_message(f"🗑️ Successfully deleted **{deleted_member_name}** from the list.")
        else:
            await interaction.response.send_message(f"❌ Error: Member \"{name}\" was not found.", ephemeral=True)


    
    @app_commands.command(name="editmember", description="Edits an existing member's information.")
    @app_commands.describe(
        name="The current full name of the member you want to edit.",
        new_name="(Optional) The new name for the member.",
        new_role="(Optional) The new role for the member."
    )
    async def edit_member(self, interaction: discord.Interaction, name: str, new_name: str = None, new_role: str = None):
    
        if new_name is None and new_role is None:
            await interaction.response.send_message("❌ Error: You must provide either a new name or a new role to update.", ephemeral=True)
            return
        
        updated_member_name = await edit_member_in_db(self.bot.db_pool, name, new_name, new_role)
        if updated_member_name:
            await interaction.response.send_message(f"✅ Successfully updated **{name}**.")
        else:
            await interaction.response.send_message(f"❌ Error: Member \"{name}\" was not found.", ephemeral=True)


    @app_commands.command(name="viewmember", description="Shows all details for a specific member, including their tasks.")
    @app_commands.describe(name="The full name of the member to view.")
    async def view_member(self, interaction: discord.Interaction, name: str):


        member_details = await get_full_member_details(self.bot.db_pool, name)

        if member_details:
            embed = discord.Embed(
                title=f"👤 Profile for {member_details['name']}",
                description=f"**Role:** {member_details['role']}",
                color=discord.Color.blue()
            )
            # Display Responsibilities
            if member_details['responsibilities']:
                resp_text = "\n".join(f"- **ID #{resp_id}:** {text}" for resp_id, text in member_details['responsibilities'])
                embed.add_field(name="Responsibilities", value=resp_text, inline=False)
            else:
                embed.add_field(name="Responsibilities", value="No responsibilities assigned.", inline=False)
            
            # Display Tasks
            if member_details['tasks']:
                tasks_text = "\n".join(f"- **Task #{task_id}:** {desc}" for task_id, desc in member_details['tasks'])
                embed.add_field(name="Pending Tasks", value=tasks_text, inline=False)
            else:
                embed.add_field(name="Pending Tasks", value="No pending tasks.", inline=False)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Error: Member \"{name}\" was not found.", ephemeral=True)
    






        
# load the Cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ManageMembers(bot))