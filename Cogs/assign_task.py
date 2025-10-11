import discord
from discord.ext import commands
import json
import os
from google import genai
from dotenv import load_dotenv

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        try:
            self.ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self.model = None
            print(f"Error initializing Gemini model: {e}")
    
    @commands.command(name="assigntask")
    async def assign_task(self, ctx, *, task_description):
        if not self.ai_client:
            await ctx.send("Sorry, the AI model is not configured correctly. Please check the API key.")
            return

        json_members_context = json.dumps(self.bot.members, indent = 2)

        # TODO ask user to put prompt rules if there is no rule don't process
        prompt_rules = """

            You are a project manager for a university computer science club. Your task is to take a new event request and break it down into smaller sub-tasks, assigning them to the correct board members.
            
            Here are your rules:
            1. After the event date is decided, assign the task "reserve room" to the Secretary.
            2. If the event requires a flyer, assign the task "Design a promotional flyer" to a member of the Marketing team.
            3. Assign the task "Post on social media" to the Marketing team.
            4. Assign the task "Announce in Discord" to the President or Vice President.
            6. The Treasurer must be assigned any tasks related to funding or budget.
            7. Try to assign different tasks to different people on the same team to distribute work.


            (If a request is too vague to assign tasks (e.g., missing a date), you must ask clarifying questions.)
        
            """

        full_prompt = (
            f"{prompt_rules}\n\n"
            f"Here is the list of board members and their responsibilities:\n{json_members_context}\n\n"
            f"Here is the new event request:\n'{task_description}'\n\n"
            "Assign the necessary tasks based on the rules."
        )

        print("--- Sending Prompt to Gemini ---")

        await ctx.send("🤖 Thinking... Please wait a moment.")

        try:
            response = self.ai_client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = full_prompt
            )
            ai_response_text = response.text
            # Send the response in chunks (Discord only accept 2000 characters)
            if len(ai_response_text) > 2000:
                for i in range(0, len(ai_response_text), 2000):
                    chunk = ai_response_text[i:i+2000]
                    await ctx.send(chunk)
            else:
                await ctx.send(ai_response_text)


        except Exception as e:
            await ctx.send(f"An error occurred while contacting the AI: {e}")
            print(f"Error generating content: {e}")


async def setup(bot):
    await bot.add_cog(Tasks(bot))
        
        
