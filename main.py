import argparse
import os
import sys

import lyricsgenius
import requests
import spotipy
from dotenv import load_dotenv
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


def build_parser():
    parser = argparse.ArgumentParser(
        description="Show the lyrics of the song currently playing on Spotify, "
        "or of any song passed as argument."
    )
    parser.add_argument(
        "title",
        nargs="?",
        help="song title to look up instead of the current playback",
    )
    parser.add_argument(
        "artist",
        nargs="?",
        help="artist of the song to look up",
    )
    return parser


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


def clean_lyrics(lyrics):
    """Drop the trailing 'Embed' line lyricsgenius leaves at the end."""
    lines = lyrics.splitlines()
    if lines and lines[-1].strip() == "Embed":
        lines.pop()
    return "\n".join(lines).rstrip()


def get_lyrics(title, artist, genius_token):
    genius = lyricsgenius.Genius(genius_token)
    try:
        song = genius.search_song(title, artist)
    except requests.RequestException as exc:
        sys.exit("Genius lookup failed: network error ({})".format(exc))
    if song is None:
        print("\nNo lyrics found on Genius for {} by {}.".format(title, artist))
        return False
    print("\n{} - {}\n".format(title, artist))
    print(clean_lyrics(song.lyrics))
    return True


def spotify_request(description, func):
    """Run a Spotify API call, turning failures into readable messages."""
    try:
        return func()
    except spotipy.SpotifyOauthError as exc:
        sys.exit(
            "{} failed: Spotify rejected the credentials in .env ({})".format(
                description, exc
            )
        )
    except spotipy.SpotifyException as exc:
        sys.exit("{} failed: Spotify API error ({})".format(description, exc))
    except requests.RequestException as exc:
        sys.exit("{} failed: network error ({})".format(description, exc))


def spotify_playback(client_id, client_secret, redirect_uri):
    scope = "user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope, cache_path=cache_file))
    results = spotify_request("Playback lookup", sp.current_playback)
    if not results or results.get("item") is None:
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
    results = spotify_request(
        "Recently played lookup",
        lambda: sp.current_user_recently_played(limit=1),
    )
    items = (results or {}).get("items") or []
    if not items:
        sys.exit("No recently played tracks on this Spotify account yet: nothing to fetch lyrics for.")
    last_song_title = items[0]["track"]["name"]
    last_song_artist = items[0]["track"]["album"]["artists"][0]["name"]
    return last_song_title, last_song_artist


def main(argv=None):
    args = build_parser().parse_args(argv)
    if bool(args.title) != bool(args.artist):
        sys.exit("Provide both a title and an artist, or neither to use the current playback.")

    client_id, client_secret, redirect_uri, genius_token = load_credentials()

    if args.title:
        found = get_lyrics(args.title, args.artist, genius_token)
        sys.exit(0 if found else 1)

    data = spotify_playback(client_id, client_secret, redirect_uri)

    if data is None:
        print("No song is being played at the moment on your Spotify account, sorry.\n")
        data = last_song_played(client_id, client_secret, redirect_uri)
        user_input = input(
            "Do you want to get the lyrics of your last played song: {} by {} ? Y/N\n".format(
                data[0], data[1]
            )
        )
        if user_input.lower() != "y":
            print("\nOk, bye.")
            return

    get_lyrics(data[0], data[1], genius_token)


if __name__ == "__main__":
    main()
