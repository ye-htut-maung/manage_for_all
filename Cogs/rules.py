import discord
from discord.ext import commands
from utils.data_manager import load_rules, save_rules

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="viewrules")
    async def view_rules(self, ctx):
        #Displays the current list of AI prompt rules.
        rules = load_rules()
        if not rules:
            await ctx.send("There are no rules defined yet. Use `>addrule` to create one.")
            return
        
        response = "📋 **Current AI Prompt Rules:**\n"
        for i, rule_text in enumerate(rules):
            response += f"**{i+1}.** {rule_text}\n"
        
        await ctx.send(response)

    @commands.command(name="addrule")
    async def add_rule(self, ctx, *, rule_text: str):
        rules = load_rules()
        # Adds a new rule to the AI prompt. 
        rules.append(rule_text)
        save_rules(rules)
        await ctx.send(f"✅ Rule added: \"{rule_text}\"")

    @commands.command(name="deleterule")
    async def delete_rule(self, ctx, rule_number: int):
        
        # Deletes a rule by its number.
        rules = load_rules()
        if not 1 <= rule_number <= len(rules):
            await ctx.send(f"Error: Invalid rule number. Please use `>viewrules` to see the list.")
            return
        
        # Adjust for zero-based index
        removed_rule = rules.pop(rule_number - 1)
        save_rules(rules)
        await ctx.send(f"🗑️ Rule #{rule_number} deleted: \"{removed_rule}\"")

async def setup(bot):
    await bot.add_cog(Rules(bot))