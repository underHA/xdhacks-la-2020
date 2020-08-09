import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

birdy_uri = '6habFhsOp2NvshLv26DqMb'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

print(spotify.track(birdy_uri))
