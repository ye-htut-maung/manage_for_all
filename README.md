Club Management & Task Assignment Bot 🤖

## Project Description

This is a Python-based Discord bot designed to help organize a university club's executive board. It acts as a smart assistant to manage member roles, track responsibilities, and delegate tasks for new events using the Google Gemini API.

The bot is designed to be secure, configurable, and persistent, storing all club data locally in a members.json file.

## How to Use the Bot

Here are the commands you can use in your designated Discord channel.

`>addmenber`

Adds a new board member to the system.

Format: >addmenber Full Name, Role

Example: >addmenber Jane Doe, President

`>listmembers`

Displays a list of all current board members and their roles.

Format: >listmembers

`>addresponsibilities`

Adds a specific responsibility to an existing member.

Format: >addresponsibilities Full Name, Responsibility Description

Example: >addresponsibilities Jane Doe, Run weekly meetings

`>assigntask`

Asks the Gemini AI to analyze a new event or project, break it down into sub-tasks, and assign them to the appropriate members based on their roles and responsibilities.

Format: >assigntask [Detailed description of the event or project]

Example: >assigntask Plan the General Interest Meeting for October 5th
