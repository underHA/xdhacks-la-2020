import discord
from discord.ext import commands

from discord.ext.commands import has_permissions, MissingPermissions

import json
import random

# Spotify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())



# Sending announcements to other servers based on the on_ready event in main
class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    user_tracks = {}
    queue = []

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

        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                # Using the Spotify API from Discord's provided track id
                # This is broken
                sp_track = sp.track(activity.track_id)
                sp_artist = sp.artist(sp_track["artists"][0]["id"])

                await ctx.send(f"{user} is listening to **{activity.title}** by {activity.artist}.\nGenres: {', '.join(sp_artist['genres'])}")
                return
        await ctx.send(f'{user} is not listening to a song.')
    

    # TODO: Figure out how to not fire more than once
    # Check if user's Spotify changed

    """
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        print("test")

        old_track = '' 
        new_track = ''

        if before.id not in Spotify.user_tracks:
            Spotify.user_tracks[str(before.id)] = ''

        # Compare before
        for activity in before.activities:
            if isinstance(activity, discord.Spotify):
                old_track = activity.track_id

        # Compare after
        for activity in after.activities:
            if isinstance(activity, discord.Spotify):
                new_track = activity.track_id

        # print(f"{old_track != new_track}, {new_track != ''}, {new_track != user_tracks[str(before.id)]}")

        # If the user changed Spotify tracks
        if old_track != new_track and new_track != '' and new_track != Spotify.user_tracks[str(after.id)]:
            # before in this context is used as Discord ID
            print(new_track)
            Spotify.user_tracks[str(after.id)] = new_track
            await self.bot.get_channel(738607027022069840).send('user changed to new track')
    """


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Spotify(bot))