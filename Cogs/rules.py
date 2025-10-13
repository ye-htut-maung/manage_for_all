import discord
from discord.ext import commands
from discord import app_commands
from utils.data_manager import get_all_rules_from_db, add_rule_to_db, delete_rule_from_db

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="viewrules", description="Displays the current list of AI prompt rules.")
    async def view_rules(self, interaction: discord.Interaction):
        #Displays the current list of AI prompt rules.
        rules = await get_all_rules_from_db(self.bot.db_pool)
        if not rules:
            await interaction.response.send_message("There are no rules defined yet. Use `/addrule` to create one.")
            return
        embed = discord.Embed(title="📋 Current AI Prompt Rules", color=discord.Color.purple())
        # Format the rules from the database records into a numbered list
        description = "\n".join(f"**{rule['id']}.** {rule['rule_text']}" for rule in rules)
        embed.description = description
        
        await interaction.response.send_message(embed=embed)
        

    @app_commands.command(name="addrule", description="Adds a new rule for the AI prompt.")
    @app_commands.describe(rule_text="The exact text of the rule you want to add.")
    async def add_rule(self,interaction: discord.Interaction, rule_text:str):
        success = await add_rule_to_db(self.bot.db_pool, rule_text)
        if success:
            await interaction.response.send_message(f"✅ Rule added: \"{rule_text}\"")
        else:
            await interaction.response.send_message("❌ An error occurred while adding the rule.", ephemeral=True)

    @app_commands.command(name="deleterule", description="Deletes a rule by its number.")
    @app_commands.describe(rule_id="The ID number of the rule to delete.")
    async def delete_rule(self, interaction: discord.Interaction, rule_id: int):
        deleted_rule_text = await delete_rule_from_db(self.bot.db_pool, rule_id)
        if deleted_rule_text:
            await interaction.response.send_message(f"🗑️ Rule #{rule_id} deleted: \"{deleted_rule_text}\"")
        else:
            await interaction.response.send_message(f"❌ Error: Rule #{rule_id} was not found.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Rules(bot))
