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

3. Install dependencies

        $ pip install -r requirements.txt

4. Run bot.py

        $ python bot.py


## MongoDB Schemas:

### Game

```
{
    "guild_id": int,
    "game_num" : int,
    "_state": str,
    "category_channel" : discord.CategoryChannel.id,
    "channels" : {
        "townsquare": discord.TextChannel.id,
        "voting-booth": discord.TextChannel.id,
        "..."
    },
    "roles": ['role_name_1', 'role_name_2', ...],
    "players": [user_id_1, user_id_2, ...]
    "phase": bool (day/night),
    "cycle": int
}
ObjectId: '_games_<guild_id>'
```

### Player

```
{
    "user_id": int,
    "guild_id": int,
    "state": str,
    "journal" : discord.TextChannel.id,
    "role": ObjectId(Role),
}
ObjectId: '_players_<user_id>_<guild_id>'
```



### Role
```
{
    "name": str,
    "type": str,
    "alignment": str,
    "night_action": bool
}
```
