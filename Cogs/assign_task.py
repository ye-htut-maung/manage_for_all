import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from google import genai
from dotenv import load_dotenv
from utils.data_manager import load_rules, save_tasks
import asyncio

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            self.model = None
            print(f"Error initializing Gemini model: {e}")
    async def _process_and_display_tasks(self, interaction: discord.Interaction, ai_response_text: str):
        # helper function to parse, save and display tasks
        try:
            # parse the json response
            clean_json_text = ai_response_text.strip().lstrip("```json").rstrip("```")
            new_tasks = json.loads(clean_json_text)

            # save the new tasks
            self.bot.tasks.extend(new_tasks)
            save_tasks(self.bot.tasks)

            # display
            embed = discord.Embed(
                title="✅ New Tasks Assigned",
                color=discord.Color.green()
            )
            for task in new_tasks:
                assignee = task.get("assigned_to", "N/A")
                task_desc = task.get("task", "No description")
                embed.add_field(name=f"👤 {assignee}", value=f"**Task:** {task_desc}", inline=False)
            
            await interaction.followup.send(embed=embed)

        except json.JSONDecodeError:
            await interaction.followup.send(
                "⚠️ **Error:** The AI returned an invalid format. Here is the raw response:\n"
                f"```\n{ai_response_text[:1800]}\n```"
            )


    
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

        output_format = """
            Your final output MUST be a valid JSON array of objects. 
            Each object represents a single task and must have three keys: "id" (an unique id for each task)
            "assigned_to" (the name of the person) 
            "task" (the description of the task) and "status"(pending for inital status). 
            Do not include any other text or explanations outside of the JSON array.
            Example Output:
            [
            {
                "id" : 1,
                "assigned_to": "Jane Doe",
                "task": "Reserve a room for the event on campus.",
                "status": "pending"
            }
            ]

            """

        initial_prompt = (
            "You are a project manager for a university computer science club. "
            "Your task is to take a new event request and break it down into smaller sub-tasks, "
            "assigning them to the correct board members based on the rules provided.\n\n"
            "Here are your rules:\n"
            f"{formatted_rules}\n\n"
            f"Here is the list of board members and their responsibilities:\n{json_members_context}\n\n"
            f"Here is the new event request:\n'{task_description}'\n\n"
            "Assign the necessary tasks based on the rules.\n"

            "If a request is too vague to assign tasks, you must ask clarifying questions.\n"
            "If you need to ask a clarifying question, your entire response must begin with the exact prefix 'QUESTIONS:' and nothing else."
            f"**Output Format(if there is no vague question):**\n{output_format}"
        )


        print("--- Sending Prompt to Gemini ---")

        # await ctx.send("🤖 Thinking... Please wait a moment.")

        try:
            response =  self.ai_client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = initial_prompt
            )
            ai_response_text = response.text


            if ai_response_text.strip().startswith("QUESTIONS:"):
                question_text = ai_response_text.replace("QUESTIONS:", "").strip()
                await interaction.followup.send(f"🤖 The AI needs more information:\n> {question_text}")

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                try:
                    # wait for 300 sec or 5 min
                    user_reply = await self.bot.wait_for('message', check = check, timeout=300.0)

                    await interaction.followup.send("🤖 Got it. Thinking again with your new information...")

                    follow_up_prompt = (
                        f"{initial_prompt}\n\n"
                        f"The user's first request was too vague. You asked: '{question_text}'\n"
                        f"The user has now provided the following additional information: '{user_reply.content}'\n\n"
                        "Please provide the final task assignments based on all this information."
                        f"**Output Format:**\n{output_format}"
                    )

                    final_response = self.ai_client.models.generate_content(
                        model = 'gemini-2.5-flash',
                        contents = follow_up_prompt
                    )
                    ai_response_text = final_response.text
                except asyncio.TimeoutError:
                    await interaction.followup.send("You took too long to reply. Please start the command again.")
                    return
            await self._process_and_display_tasks(interaction, ai_response_text)

            # Send the response in chunks (Discord only accept 2000 characters)
            # Use followup.send() for all messages after defer()
            # if len(ai_response_text) > 2000:
            #     for i in range(0, len(ai_response_text), 2000):
            #         chunk = ai_response_text[i:i+2000]
            #         await interaction.followup.send(chunk)
            # else:
            #     await interaction.followup.send(ai_response_text)


        except Exception as e:
            await interaction.followup.send(f"An error occurred while contacting the AI: {e}")
            print(f"Error generating content: {e}")

    @app_commands.command(name="tasks", description="View all pending tasks or tasks from a specific member")
    @app_commands.describe(member="(Optional) The member whose tasks you want to see.")
    async def view_tasks(self, interaction: discord.Interaction, member: str = None):
        tasks=self.bot.tasks
        pending_tasks = [t for t in tasks if t.get("status", "pending") == "pending"]

        if not pending_tasks:
            await interaction.response.send_message("There are no pending tasks!")
            return
        embed = discord.Embed(title="Pending Tasks", color=discord.Color.blue())

        if member:
            member_tasks = [t for t in pending_tasks if t.get("assigned_to", "").lower() == member.lower()]

            if not member_tasks:
                await interaction.response.send_message(f"No pending tasks found for **{member}**.")
                return
            embed.title = f"Pending Tasks for {member}"
            tasks_to_display = member_tasks
        else:
            tasks_to_display = pending_tasks
        for task in tasks_to_display:
            task_id = task.get("id", "N/A")
            task_desc = task.get("task", "No description")
            assignee = task.get("assigned_to", "N/A")
            embed.add_field(
                name=f"Task #{task_id} (Assigned to: {assignee})", 
                value=task_desc, 
                inline=False
            )
    
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="completetask", description="Marks a task as complete by its ID.")
    @app_commands.describe(task_id="The ID number of the task to complete.")
    async def complete_task(self, interaction: discord.Interaction, task_id: int):
        task_found = False
        for task in self.bot.tasks:
            if task.get("id") == task_id:
                task["status"] = "complete"
                task_found = True
                break
        
        if task_found:
            save_tasks(self.bot.tasks)
            await interaction.response.send_message(f"✅ Task #{task_id} has been marked as complete.")
        else:
            await interaction.response.send_message(f"❌ Error: Task #{task_id} was not found.", ephemeral=True)


    @app_commands.command(name="addtask", description="Manually adds a new task.")
    @app_commands.describe(member="The name of the member to assign the task to.", description="The description of the task.")
    async def add_task(self, interaction: discord.Interaction, member: str, description: str):
        # Find the highest existing ID to create a new unique ID
        # TODO find better way to generate id
        new_id = max([t.get("id", 0) for t in self.bot.tasks] + [0]) + 1

        new_task = {
            "id": new_id,
            "assigned_to": member,
            "task": description,
            "status": "pending"
        }
        
        self.bot.tasks.append(new_task)
        save_tasks(self.bot.tasks)
        
        await interaction.response.send_message(f"✅ Manually added Task #{new_id} for **{member}**.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
        
        
