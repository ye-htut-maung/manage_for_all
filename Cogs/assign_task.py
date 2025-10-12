import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from google import genai
from dotenv import load_dotenv
from utils.data_manager import load_rules

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
        try:
            self.ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self.model = None
            print(f"Error initializing Gemini model: {e}")
    
    @app_commands.command(name="assigntask", description="Uses AI to assign tasks for a new event")
    @app_commands.describe(task_description="A detailed description of the event or project to be planned.")
    async def assign_task(self,interaction:discord.Interaction, task_description:str):
        if not self.ai_client:
            await interaction.response.send_message("Sorry, the AI model is not configured correctly. Please check the API key.")
            return
        rules = load_rules()
        if not rules:
            await interaction.response.send_message("⚠️ **Error:** No prompt rules are defined. A user must add rules using the `>addrule` command before tasks can be assigned.")
            return

        # Use defer() to acknoledge the command and show a "Thinking..." state
        await interaction.response.defer()

        formatted_rules = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))

        json_members_context = json.dumps(self.bot.members, indent = 2)

        full_prompt = (
            "You are a project manager for a university computer science club. "
            "Your task is to take a new event request and break it down into smaller sub-tasks, "
            "assigning them to the correct board members based on the rules provided.\n\n"
            "Here are your rules:\n"
            f"{formatted_rules}\n\n"
            f"Here is the list of board members and their responsibilities:\n{json_members_context}\n\n"
            f"Here is the new event request:\n'{task_description}'\n\n"
            "Assign the necessary tasks based on the rules."
        )


        print("--- Sending Prompt to Gemini ---")

        # await ctx.send("🤖 Thinking... Please wait a moment.")

        try:
            response = self.ai_client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = full_prompt
            )
            ai_response_text = response.text
            # Send the response in chunks (Discord only accept 2000 characters)
            # Use followup.send() for all messages after defer()
            if len(ai_response_text) > 2000:
                for i in range(0, len(ai_response_text), 2000):
                    chunk = ai_response_text[i:i+2000]
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(ai_response_text)


        except Exception as e:
            await interaction.followup.send(f"An error occurred while contacting the AI: {e}")
            print(f"Error generating content: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
        
        
