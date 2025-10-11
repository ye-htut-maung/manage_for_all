import json

def save_members_to_json(self):
    # Saves the members list to members.json.
    # TODO: when you write the file, don't overwrite everything
    with open('members.json', 'w') as f:
        json.dump(self.bot.members, f, indent = 4)