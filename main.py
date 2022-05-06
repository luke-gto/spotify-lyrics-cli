from functools import cache
import lyricsgenius
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))
env_file = script_directory + "/.env"


def load_credentials():

    if os.path.isfile(script_directory + "/.env"):

        dotenv_path = script_directory + "/.env"
        load_dotenv(dotenv_path)
        SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
        SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
        SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")
        GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN")

        if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI != "":

            print("Valid credentials found!")
            return (
                SPOTIPY_CLIENT_ID,
                SPOTIPY_CLIENT_SECRET,
                SPOTIPY_REDIRECT_URI,
                GENIUS_TOKEN,
            )

        else:
            print("Credentials not valid. Pleae try again.")


def get_lyrics(title, artist):

    genius = lyricsgenius.Genius(os.environ["GENIUS_TOKEN"])

    song = genius.search_song(title, artist)

    print("\n" + song.lyrics)


def spotify_playback(SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI):
    scope = "user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope, cache_path="./cache.txt"))

    results = sp.current_playback()
    if results == None:

        return None

    else:
        title = results["item"]["name"]
        artist = results["item"]["artists"][0]["name"]

        return title, artist


def last_song_played(SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI):
    scope = "user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope, cache_path="./cache.txt"))
    results = sp.current_user_recently_played(limit=1)
    last_song_title = results["items"][0]["track"]["name"]
    last_song_artist = results["items"][0]["track"]["album"]["artists"][0]["name"]
    return last_song_title, last_song_artist


if __name__ == "__main__":

    credentials = load_credentials()

    data = spotify_playback(credentials[0], credentials[1], credentials[2])

    if data == None:
        data = last_song_played(credentials[0], credentials[1], credentials[2])
        print("No song is being played at the moment on your Spotify account, sorry.\n")
        user_input = input(
            "Do you want to get the lyrics of your last played song: {} by {} ? Y/N\n".format(
                data[0], data[1]
            )
        )
        if user_input.lower() == "y":
            get_lyrics(data[0], data[1])
        else:
            print("\nOk, bye.")
            sys.exit()
    else:
        get_lyrics(data[0], data[1])
