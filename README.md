# Werewolf Mod 2

To run the bot:

1. Create a `.env` file, and add:

        echo "TOKEN = your-bot-token-from-discord" > .env
        echo "GUILD_ID = guild-to-test-bot" >> .env


2. Create virtual env using method of choice

        # Using venv

        $ python3 -m venv <path-to-venv>

        $ source <path-to-venv>/bin/activate

        # Using Conda

        $ conda create -n <env-name> python=3.10

        $ conda activate <env-name>

2. Install dependencies

        $ pip install -r requirements.txt

2. Run bot.py

        $ python bot.py
