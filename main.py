import os
import sys

import lyricsgenius
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

script_directory = os.path.dirname(os.path.realpath(__file__))
env_file = os.path.join(script_directory, ".env")
cache_file = os.path.join(script_directory, ".cache.txt")

CREDENTIAL_KEYS = (
    "SPOTIPY_CLIENT_ID",
    "SPOTIPY_CLIENT_SECRET",
    "SPOTIPY_REDIRECT_URI",
    "GENIUS_TOKEN",
)


def load_credentials():
    """Read and validate the credentials from the .env file next to the script."""
    if not os.path.isfile(env_file):
        sys.exit(
            "No .env file found next to the script. Copy .env.example to .env "
            "and fill in your Spotify and Genius credentials (see README)."
        )

    load_dotenv(env_file)
    values = {key: (os.environ.get(key) or "").strip() for key in CREDENTIAL_KEYS}

    empty = [key for key, value in values.items() if not value]
    placeholders = [
        key for key, value in values.items() if value and "YOUR" in value.upper()
    ]
    if empty or placeholders:
        bad = ", ".join(empty + placeholders)
        sys.exit(
            "Credentials not valid: {} are empty or still contain the example "
            "placeholders. Edit {} and see the README.".format(bad, env_file)
        )

    print("Valid credentials found!")
    return (
        values["SPOTIPY_CLIENT_ID"],
        values["SPOTIPY_CLIENT_SECRET"],
        values["SPOTIPY_REDIRECT_URI"],
        values["GENIUS_TOKEN"],
    )


def get_lyrics(title, artist, genius_token):
    genius = lyricsgenius.Genius(genius_token)
    song = genius.search_song(title, artist)
    if song is None:
        print("\nNo lyrics found on Genius for {} by {}.".format(title, artist))
        return
    print("\n" + song.lyrics)


def spotify_playback(client_id, client_secret, redirect_uri):
    scope = "user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope, cache_path=cache_file))
    results = sp.current_playback()
    if results is None:
        return None

    title = results["item"]["name"]
    artist = results["item"]["artists"][0]["name"]
    return title, artist


def last_song_played(client_id, client_secret, redirect_uri):
    scope = "user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope, cache_path=cache_file))
    results = sp.current_user_recently_played(limit=1)
    items = (results or {}).get("items") or []
    if not items:
        sys.exit("No recently played tracks on this Spotify account yet: nothing to fetch lyrics for.")
    last_song_title = items[0]["track"]["name"]
    last_song_artist = items[0]["track"]["album"]["artists"][0]["name"]
    return last_song_title, last_song_artist


if __name__ == "__main__":

    client_id, client_secret, redirect_uri, genius_token = load_credentials()

    data = spotify_playback(client_id, client_secret, redirect_uri)

    if data is None:
        print("No song is being played at the moment on your Spotify account, sorry.\n")
        data = last_song_played(client_id, client_secret, redirect_uri)
        user_input = input(
            "Do you want to get the lyrics of your last played song: {} by {} ? Y/N\n".format(
                data[0], data[1]
            )
        )
        if user_input.lower() == "y":
            get_lyrics(data[0], data[1], genius_token)
        else:
            print("\nOk, bye.")
            sys.exit()
    else:
        get_lyrics(data[0], data[1], genius_token)
