import discord
import os
from dotenv import load_dotenv
import json
from google import genai
from discord.ext import commands


# ----- SETUP -----
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
allowed_ids_str = os.getenv('ALLOWED_CHANNEL_IDS')
if allowed_ids_str:
    ALLOWED_CHANNEL_IDS = [int(id_str) for id_str in allowed_ids_str.split(',')]
else:
    ALLOWED_CHANNEL_IDS = []
    print("WARNING: ALLOWED_CHANNEL_IDS was not found in the .env file.")

# ----- BOT INITIALIZATION -----
# This is needed to let the bot read message content
intents = discord.Intents.default()
intents.message_content = True

# change client to commands.Bot to get comamnd handling
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix = '>', intents = intents) # Prefix is now fallback

# ----- GLOBAL CHECK -----
# A global check to ensure commands only run in allowed channels
@bot.check
async def restrict_to_all_channels(ctx):
    return ctx.channel.id in ALLOWED_CHANNEL_IDS

# ----- DATA LOADING -----
# attach the 'members' list to the bot itself so Cogs can access it
try:
    with open('members.json', 'r') as f:
        bot.members = json.load(f)
    print("Members data loaded successfully.")
except(FileNotFoundError, json.JSONDecodeError):
    bot.members=[]
    print("members.json not found or empty, starting with an empty list.")

# ----- COG LOADING & READY EVENT -----

@bot.event
async def on_ready():
    # This message prints in your terminal when the bot is online
    print(f'We have logged in as {bot.user}')
    # Load all .py files in the Cogs folder and loads them.
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"Cogs.{filename[:-3]}")
            print(f'Loaded Cog: {filename}')
    # Sync the command tree
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


# ----- RUN THE BOT -----
bot.run(TOKEN)


# save members to member.json
# def save_members():
#     with open('members.json', 'w') as f:
#         json.dump(members, f, indent = 4)

# @bot.event
# async def on_message(message):
#     # only work in specific channel
#     if message.channel.id not in ALLOWED_CHANNEL_IDS:
#         return

#     # Ignore messages sent by the bot itself
#     if message.author == client.user:
#         return


#     # Respond to a specific message
#     if message.content.startswith('>hello'):
#         await message.channel.send('Hello there!')

#     # Add member to the bot
#     # eg. >addmember Kate, President
#     if message.content.startswith('>addmember'):
#         command_content = message.content[len('>addmember '):]
#         parts = command_content.split(',')
#         if len(parts) == 2:
#             name = parts[0].strip()
#             role = parts[1].strip()

#             member_data = {'name': name, 'role': role, 'responsibilities': []}
#             members.append(member_data)
#             save_members()
#             await message.channel.send(f'Added **{name}** as **{role}**')
#             # for debug
#             print(f"Current members: {members}")
#         else:
#             await message.channel.send("Please use the format: `>addmember Full Name, Role`")

#     # list members
#     if message.content.startswith('>listmembers'):
#         if not members:
#             await message.channel.send("There are no members in the list yet.")
#             return

#         response = "Here are the current board members:\n"
#         for member in members:
#             response += f"- {member['name']}: {member['role']}\n"

#         await message.channel.send(response)


#     # add responsibilities
#     if message.content.startswith('>addresponsibilities'):
#         command_content = message.content[len('>addresponsibilities '):]
#         parts = command_content.split(',')
#         if len(parts) == 2:
#             name = parts[0].strip()
#             responsibility = parts[1].strip()
#             found = False
#             # search member
#             # TODO: update search runtime
#             for member in members:
#                 if member["name"] == name:
#                     member["responsibilities"].append(responsibility)
#                     found = True
#             if not found:
#                 await message.channel.send(f'The member is not added')
#                 return

#             save_members()
#             await message.channel.send(f'Added **{name}**\'s responsibility as **{responsibility}**')
#             # for debug
#             print(f"Current members: {members}")
#         else:
#             await message.channel.send("Please use the format: `>addmember Full Name, Responsibility`")

#     # assign task
#     if message.content.startswith('>assigntask'):
#         task_description = message.content[len('>assigntask '):]

#         # convert dict to string
#         prompt_context = json.dumps(members)
        

#         prompt_rules = """You are a project manager for a university computer science club. Your task is to take a new event request and break it down into smaller sub-tasks, assigning them to the correct board members.
        
#         Here are your rules:
#         After the event date is decided, assign the task "reserve room" to the Secretary.
#         If the event requires a flyer, assign the task "Design a promotional flyer" to a member of the Marketing team.
#         Assign the task "Post on social media" to the Marketing team.
#         Aassign the task "Announce in Discord" to the President or Vice President.
#         If a request is too vague to assign tasks (e.g., it's missing a date or budget), you must ask clarifying questions.
#         Treasurer needs to manage Financial related things
#         Do not ask question.
#         Assign the necessary tasks based on the rules.
#         It is better to assign different person on a same team for the different task.
#         """

#         full_prompt = f"{prompt_rules}\n\nHere is the list of board members:\n{prompt_context}\n\nHere is the new event request:\n{task_description}"

#         print("--- Sending Prompt to Gemini ---")
#         print(full_prompt)
#         print("--------------------------------")

#         await message.channel.send("🤖 Thinking... Please wait a moment.")

#         ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#         response = ai_client.models.generate_content(
#             model = 'gemini-2.5-flash',
#             contents = full_prompt
#         )

#         ai_response_text = response.text
        
#         # Send the response in chunks (Discord only accept 2000 characters)
#         if len(ai_response_text) > 2000:
#             # If the message is too long, split it into chunks of 2000 characters
#             for i in range(0, len(ai_response_text), 2000):
#                 chunk = ai_response_text[i:i+2000]
#                 await message.channel.send(chunk)
#         else:
#             # If the message is short enough, send it normally
#             await message.channel.send(ai_response_text)







