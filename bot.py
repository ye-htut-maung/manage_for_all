import discord
import os
from dotenv import load_dotenv
import json

# load .env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_CHANNEL_ID = os.getenv('ALLOWED_CHANNEL_ID')


# This is needed to let the bot read message content
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

members = []

@client.event
async def on_ready():
    global members # I use global as if I need to reassign to empyt list, it will refer to the global scope

    try:
        with open('members.json', 'r') as f:
            members = json.load(f)
        print("Members data loaded successfully.")
    except FileNotFoundError:
        print("member.json not found, starting with an empty list.")
    except json.JSONDecodeError:
        # if a file is empty
        print("members.json is empty or give error while decoding, starting with an empty list")
        members = []
    # This message prints in your terminal when the bot is online
    print(f'We have logged in as {client.user}')

# save members to member.json
def save_members():
    with open('members.json', 'w') as f:
        json.dump(members, f, indent = 4)

@client.event
async def on_message(message):
    # only work in specific channel
    if message.channel.id != int(ALLOWED_CHANNEL_ID):
        return

    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return


    # Respond to a specific message
    if message.content.startswith('>hello'):
        await message.channel.send('Hello there!')

    # Add member to the bot
    # eg. >addmember Kate, President
    if message.content.startswith('>addmember'):
        command_content = message.content[len('>addmember '):]
        parts = command_content.split(',')
        if len(parts) == 2:
            name = parts[0].strip()
            role = parts[1].strip()

            member_data = {'name': name, 'role': role, 'responsibilities': []}
            members.append(member_data)
            save_members()
            await message.channel.send(f'Added **{name}** as **{role}**')
            # for debug
            print(f"Current members: {members}")
        else:
            await message.channel.send("Please use the format: `>addmember Full Name, Role`")

    # list members
    if message.content.startswith('>listmembers'):
        if not members:
            await message.channel.send("There are no members in the list yet.")
            return

        response = "Here are the current board members:\n"
        for member in members:
            response += f"- {member['name']}: {member['role']}\n"

        await message.channel.send(response)


    # add responsibilities
    if message.content.startswith('>addresponsibilities'):
        command_content = message.content[len('>addresponsibilities '):]
        parts = command_content.split(',')
        if len(parts) == 2:
            name = parts[0].strip()
            responsibility = parts[1].strip()
            found = False
            # search member
            # TODO: update search runtime
            for member in members:
                if member["name"] == name:
                    member["responsibilities"].append(responsibility)
                    found = True
            if not found:
                await message.channel.send(f'The member is not added')
                return

            save_members()
            await message.channel.send(f'Added **{name}**\'s responsibility as **{responsibility}**')
            # for debug
            print(f"Current members: {members}")
        else:
            await message.channel.send("Please use the format: `>addmember Full Name, Responsibility`")

# Run the bot using your secret token
client.run(TOKEN)
