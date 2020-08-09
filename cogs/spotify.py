import discord
from discord.ext import commands

from discord.ext.commands import has_permissions, MissingPermissions

import json
import random

# Spotify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

badList = ["pop", "edm", "r&b", "rap", "trap", "hip hop", "metal", "punk", "rock"]

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
                genres = sp_artist['genres']

                await ctx.send(f"{user} is listening to **{activity.title}** by {activity.artist}.\nGenres: {', '.join(genres)}")
                return
        await ctx.send(f'{user} is not listening to a song.')
    

    # TODO: Figure out how to not fire more than once if in multiple servers
    # Check if user's Spotify changed
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        old_track = '' 
        new_track = ''

        track_activity = {}

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
                track_activity = activity


        # If the user changed Spotify tracks
        if old_track != new_track and new_track != '' and new_track != Spotify.user_tracks[str(after.id)]:
            # before in this context is used as Discord ID
  

            # If we got here, then the bot can detect if a user switches to a new song
            Spotify.user_tracks[str(after.id)] = new_track

            sp_track = sp.track(activity.track_id)
            sp_artist = sp.artist(sp_track["artists"][0]["id"])
            genres = sp_artist['genres']


            # Posts a message in testing everytime a new song is played
            # To retrieve genres: 
            await self.bot.get_channel(741774089232056472).send(f"{after} is now listening to **{activity.title}** by {activity.artist}.\nGenres: {', '.join(genres)}")
            
            if any(g in genre for genre in genres for g in badList):
                await self.bot.get_user(id=int(after.id)).send("It looks like you are listening to a song that could decrease your productivity.")
        


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Spotify(bot))