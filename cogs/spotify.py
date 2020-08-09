import discord
from discord.ext import commands

from discord.ext.commands import has_permissions, MissingPermissions

import json
import random

# Mongo

import pymongo
from pymongo import MongoClient

# For environment variables
import os
cluster = MongoClient(os.environ.get('MONGO_KEY'))

db = cluster["soundmood"]
collection = db["stats"]
optout = db["optout"]

# Spotify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

badList = ["edm", "r&b", "rap", "trap", "hip hop", "metal", "punk"]
goodList = ["jazz", "classical", "lo-fi", "chill"]

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

        if optout.find_one({"id_":after.id}):
            # If the user has opted out, don't go through
            return


        old_track = '' 
        new_track = ''

        # Check if user is already in database, add them if not
        if not collection.find_one({"id_":after.id}):
            collection.insert_one({"id_":after.id, "streak": 0, "track": ""})

        # Compare before
        for activity in before.activities:
            if isinstance(activity, discord.Spotify):
                old_track = activity.track_id

        # Compare after
        for activity in after.activities:
            if isinstance(activity, discord.Spotify):
                new_track = activity.track_id


        user = collection.find_one({"id_":after.id})

        # If the user changed Spotify tracks
        if old_track != new_track and new_track != '' and new_track != user["track"]:
            # before in this context is used as Discord ID
  
            # If we got here, then the bot can detect if a user switches to a new song
            # Update track on mongoDB
            collection.update_one({"id_": after.id}, {"$set": {"track": new_track}})

            sp_track = sp.track(activity.track_id)
            sp_artist = sp.artist(sp_track["artists"][0]["id"])
            genres = sp_artist['genres']


            # Posts a message in testing everytime a new song is played
            # To retrieve genres: 
            await self.bot.get_channel(741774089232056472).send(f"{after} is now listening to **{activity.title}** by {activity.artist}.\nGenres: {', '.join(genres)}")
            
            if any(g in genre for genre in genres for g in badList):
                # Check if they have a streak
                streak_string = ''
                if user["streak"] != 0:
                    streak_string = f'\n😥 You lost your {user["streak"]} song Soundness Streak! Try playing a few songs beneficial your wellness to build it back up again.'

                await self.bot.get_user(id=int(after.id)).send(f"It looks like you are listening to a song that could decrease your productivity.{streak_string}")

                # Set user's wellness song streak to 0
                collection.update_one({"id_": after.id}, {"$set": {"streak": 0}})
            else:
                # Else, increment their song streak
                collection.update_one({"id_": after.id}, {"$inc": {"streak": 1}})

                new_user = collection.find_one({"id_":after.id})
                
                # If their streak is a multiple of 5, congratulate them
                if new_user["streak"] % 5 == 0:
                    await self.bot.get_user(id=int(after.id)).send(f"You're on a {new_user['streak']} song Soundness Streak 🔥! Keep it up!")
        

    @commands.command(name="optout")
    async def optout(self, ctx):
        optout.insert_one({"_id": ctx.author.id})
        await ctx.send(f"You have **opted out** of A Sound Mood. To join the program again, use ?optin.")

    @commands.command(name="optin")
    async def optin(self, ctx):
        optout.delete_one({"_id": ctx.author.id})
        await ctx.send(f"You have **opted into** A Sound Mood. To leave the program, use ?optout.")

    @commands.command(name="activity", aliases=["recommend"])
    async def activity(self, ctx, activity:str):
        await ctx.send(f"hi, you want {activity}?")

    @activity.error
    async def activity_error(self, ctx, error):
        await ctx.send('Please specify what activity you\'re working on!\nExample: ?activity homework')

    @commands.command(name="stats", aliases=["stat", "score"])
    async def stats(self, ctx, user: discord.Member=None):
        user = user or ctx.author

        if optout.find_one({"_id": user.id}) or not collection.find_one({"id_":user.id}):
            await ctx.send(f"Sorry, that user has either opted out or is not in our system!")
        else:
            embed = discord.Embed(title=f"{user}'s Soundness Score",
                color=random.randint(0, 0xFFFFFF))
        
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Streak", value=collection.find_one({"id_":user.id})["streak"])

            embed.set_footer(text=f"Requested by @{ctx.message.author}", icon_url=ctx.message.author.avatar_url)

            await ctx.send('', embed=embed)


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Spotify(bot))