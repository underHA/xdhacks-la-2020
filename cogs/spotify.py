import discord
from discord.ext import commands

from discord.ext.commands import has_permissions, MissingPermissions

import json
import random

# Spotify

"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
"""

# Sending announcements to other servers based on the on_ready event in main
class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='spotify', aliases=['sptfy'])
    async def spotify(self, ctx):
        """
        Check what song someone is playing on Spotify.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command passed...')

    @spotify.command()
    async def check(self, ctx, user: discord.Member=None):
        user = user or ctx.author
        print(user.activities)
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                # Using the Spotify API from Discord's provided track id
                # This is broken
                # track = sp.track(f'spotify:track:{activity.track_id}')
                # print(track)

                await ctx.send(f"{user} is listening to **{activity.title}** by {activity.artist}.")
                return
        await ctx.send(f'{user} is not listening to a song.')


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Spotify(bot))