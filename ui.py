import discord
import random

from discord import ui, Interaction

from config import CHANNEL_CONFIG, GameState

class ChannelSelectDropdown(ui.Select):
    def __init__(self, game):
        super().__init__()

        options = [
            discord.SelectOption(label=channel, default=config.get('default', False))
            for channel, config in CHANNEL_CONFIG[GameState.NEW].items()
        ]

        self.current_game = game

        super().__init__(min_values=1, max_values=len(options), options=options)


    async def callback(self, interaction: Interaction):
        # self.disabled = True
        assert self.view is not None
        if self.current_game.channels == {}:
            self.current_game.channels = {channel_name: {'name': f'g{self.current_game.id}-{channel_name}'} for channel_name in self.values}
        await self.current_game.create_channels(interaction)
        await interaction.response.send_message('Game creation complete!')
        self.disabled = True
        return self.current_game

class ChannelSelectView(ui.View):
    def __init__(self, game):
        super().__init__()
        self.add_item(ChannelSelectDropdown(game))


class ConfirmationView(ui.View):

    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.confirmed = False
        self.interaction = interaction

    @ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.confirmed = True
        self.interaction = interaction
        self.stop()

    @ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        self.interaction = interaction
        self.stop()

    async def on_timeout(self):
        self.stop()
        await self.interaction.edit_original_response(view=None)
        await self.interaction.followup.send('Confirmation timed out. Cancelling...', ephemeral=True)


class RoleModal(ui.Modal, title='Role List'):
    roles = ui.TextInput(
        label='Role List',
        style=discord.TextStyle.paragraph,
        required=True,
        placeholder='''
Villager
Villager
Villager
''')

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message('Roles Set.')
        self.roles = random.shuffle(self.roles.value.split('\n'))

        return self.roles
