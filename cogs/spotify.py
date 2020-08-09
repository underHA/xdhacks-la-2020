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

recommendations = {
    "homework": ["https://open.spotify.com/playlist/0vvXsWCC9xrXsKd4FyS8kM?si=2KgUX9YWQpKlONqAhHLnXg", "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn?si=pG_GlF0DQs2NSr3QuGRtzg", "https://open.spotify.com/playlist/5FmmxErJczcrEwIFGIviYo?si=VX6gnAMtRv-7EKHEi-LLaA"],
    "meditation": ["https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u?si=Qm89fctiT_mtmin_BAQwHg", "https://open.spotify.com/playlist/37i9dQZF1DX9uKNf5jGX6m?si=GzFEJTTBTyaqoc4I8_0SYg","https://open.spotify.com/playlist/37i9dQZF1DX1tuUiirhaT3?si=HAQSjuvTSSeEh7O11_Fb5A"],
    "driving": ["https://open.spotify.com/playlist/37i9dQZF1DX9wC1KY45plY?si=6a-1Cyq0SESYd2bK3hVjtw", "https://open.spotify.com/playlist/37i9dQZF1DWWiDhnQ2IIru?si=aOvv-eB4TS6FFjorvuIDfA","https://open.spotify.com/playlist/37i9dQZF1DXdOEFt9ZX0dh?si=w5zgsJmGQPKVxZwmqljtHA"],
    "exercise": ["https://open.spotify.com/playlist/37i9dQZF1DXdejmG21jbny?si=-apGiFVTRUCJDs2l06aOMw", "https://open.spotify.com/playlist/37i9dQZF1DWUI1rlvkdQnb?si=wWdQf-z-TwOHxHl8Xp26UA", "https://open.spotify.com/playlist/37i9dQZF1DX4Y1uAfxGdKJ?si=lIopcXBYRHmWSiUW8B-NaA"],
    "workout": ["https://open.spotify.com/playlist/37i9dQZF1DXdejmG21jbny?si=-apGiFVTRUCJDs2l06aOMw", "https://open.spotify.com/playlist/37i9dQZF1DWUI1rlvkdQnb?si=wWdQf-z-TwOHxHl8Xp26UA", "https://open.spotify.com/playlist/37i9dQZF1DX4Y1uAfxGdKJ?si=lIopcXBYRHmWSiUW8B-NaA"],
}

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
            await ctx.send('Invalid command passed. Use the `?help spotify` command to learn more.')

    @spotify.command()
    async def check(self, ctx, user: discord.Member=None):
        """
        Check what song a user is playing on Spotify with its associated genres.
        """
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
            collection.insert_one({"id_":after.id, "streak": 0, "track": "", "wellness": 50})

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

                # Wellness score
                collection.update_one({"id_": after.id}, {"$inc": {"wellness": -7}})


            else:
                # Else, increment their song streak
                collection.update_one({"id_": after.id}, {"$inc": {"streak": 1}})

                # Wellness score
                collection.update_one({"id_": after.id}, {"$inc": {"wellness": 4}})

                new_user = collection.find_one({"id_":after.id})
                
                # If their streak is a multiple of 5, congratulate them
                if new_user["streak"] % 5 == 0:
                    await self.bot.get_user(id=int(after.id)).send(f"You're on a {new_user['streak']} song Soundness Streak 🔥! Keep it up!")
        

    @commands.command(name="optout")
    async def optout(self, ctx):
        """
        Opt-out of A Sound Mind.
        """
        optout.insert_one({"_id": ctx.author.id})
        await ctx.send(f"You have **opted out** of A Sound Mood. To join the program again, use ?optin.")

    @commands.command(name="optin")
    async def optin(self, ctx):
        """
        Opt into A Sound Mind.
        """
        optout.delete_one({"_id": ctx.author.id})
        await ctx.send(f"You have **opted into** A Sound Mood. To leave the program, use ?optout.")

    @commands.command(name="activity", aliases=["recommend"])
    async def activity(self, ctx, activity:str):
        """
        Recommends playlists based on your activity.
        Currently supported activities: homework, meditation, driving, exercise, workout
        """
        if activity.lower() not in recommendations.keys():
            await ctx.send(f"Sorry, I don't have a playlist for that! Maybe you could try `?activity {random.choice(list(recommendations.keys()))}`.")
        else:

            playlists = ''
            
            for i in range(len(recommendations[activity.lower()])): 
                playlists += f'\n[Playlist {i+1}]({recommendations[activity.lower()][i]})'

            embed = discord.Embed(title=f"A Sound Mood's Recommendations for {activity.lower()}",
                description=playlists,
                color=random.randint(0, 0xFFFFFF))

            embed.set_footer(text=f"Requested by @{ctx.message.author}", icon_url=ctx.message.author.avatar_url)

            await ctx.send('', embed=embed)

    @activity.error
    async def activity_error(self, ctx, error):
        await ctx.send('Please specify what activity you\'re working on!\nExample: ?activity homework')

    @commands.command(name="stats", aliases=["stat", "score"])
    async def stats(self, ctx, user: discord.Member=None):
        """
        Check your Soundness Streak or another user's Soundness.
        """
        user = user or ctx.author

        if optout.find_one({"_id": user.id}) or not collection.find_one({"id_":user.id}):
            await ctx.send(f"Sorry, that user has either opted out or is not in our system!")
        else:
            embed = discord.Embed(title=f"{user}'s Soundness Score",
                color=random.randint(0, 0xFFFFFF))
        
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Streak", value=f'{collection.find_one({"id_":user.id})["streak"]} songs')
            embed.add_field(name="Wellness Score", value=collection.find_one({"id_":user.id})["wellness"])

            embed.set_footer(text=f"Requested by @{ctx.message.author}", icon_url=ctx.message.author.avatar_url)

            await ctx.send('', embed=embed)


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Spotify(bot))