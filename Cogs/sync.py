from discord.ext import commands

class Sync(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @commands.command()

    # This built-in command check is to restrict this command to the bot's owner.
    # TODO I will change later that each owner of the bot or the admin can be assigned by the bot owner

    async def sync(self, ctx:commands.Context, scope: str="global"):
        # >sync global -> syncs to all servers (takes long)
        # >sync guild -> syncs to the current server instantly 
        if scope.lower() == "guild":
            cmds = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ Synced {len(cmds)} commands to this guild.")
            print(f"Synced {len(cmds)} commands to {ctx.guild.name}.")
            return
        if scope.lower() == "global":
            fmt = await self.bot.tree.sync()
            await ctx.send(f"✅ Synced {len(fmt)} commands globally.")
            print(f"Synced {len(fmt)} commands globally.")
            return
        await ctx.send("Invalid scope. Please use `guild` or `global`.")

async def setup(bot:commands.Bot):
    await bot.add_cog(Sync(bot))