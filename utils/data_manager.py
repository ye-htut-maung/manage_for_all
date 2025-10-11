import json

def save_members_to_json(self):
    # Saves the members list to members.json.
    # TODO: when you write the file, don't overwrite everything
    with open('members.json', 'w') as f:
        json.dump(self.bot.members, f, indent = 4)

def load_rules():
    #Loads the list of rules from rules.json.
    try:
        with open('rules.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # Return an empty list if file is missing or empty

def save_rules(rules_list):
    #Saves a list of rules to the rules.json file.
    with open('rules.json', 'w') as f:
        json.dump(rules_list, f, indent=4)