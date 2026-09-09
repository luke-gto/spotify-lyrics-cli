# spotify-lyrics-cli

Simple Python script to quickly show on the terminal the lyrics of the song that is being currently played on Spotify, or of any song you pass on the command line.

## Installation

1. Create a Python virtual environment to not mess around with the Python installation that's part of your OS.

2. Install the dependencies with ```pip install -r requirements.txt```

3.  You need to put the credentials for accessing the [Spotify Web API](https://developer.spotify.com/dashboard/login) Spotify Web API and the [Genius API](http://genius.com/api-clients) Genius API in the ```.env``` file. Copy the template and fill it in:

	```
	cp .env.example .env
	```

		SPOTIPY_CLIENT_ID='YOUR CLIENT ID HERE'
		SPOTIPY_CLIENT_SECRET='YOUR CLIENT SECRET HERE'
		SPOTIPY_REDIRECT_URI='YOUR REDIRECT URI HERE'
		GENIUS_TOKEN='YOUR TOKEN HERE'

	The ```.env``` file is git-ignored: never commit your real credentials. In the Spotify dashboard, register ```SPOTIPY_REDIRECT_URI``` (for example ```http://localhost:8888/callback```) as a redirect URI of your app.

## Usage

```
python main.py                      # lyrics of the current playback
python main.py "Song title" "Artist"  # lyrics of any song
```

- The first run opens a browser page to authorize your Spotify account; the token is then cached in ```.cache.txt``` next to the script, so it only happens once.
- If nothing is playing, the script proposes the lyrics of your last played song.
- The script is more handy if you can launch it with a [shell alias](https://en.wikipedia.org/wiki/Alias_(command)), for example:

  ```
  alias lyrics='python /full/path/to/spotify-lyrics-cli/main.py'
  ```

  and then just type ```lyrics``` while a song is playing.

## Troubleshooting

- **"No .env file found" / "Credentials not valid"**: follow step 3 above; the message names the missing or placeholder keys.
- **"Spotify rejected the credentials"**: client id/secret do not match your Spotify app, or the redirect URI in ```.env``` is not registered in the app settings.
- **"No lyrics found on Genius"**: the Genius search came up empty; try the exact title and artist with the two-argument form.
- Exit codes: 0 success, 1 no lyrics found, 1 with a message for configuration, authentication or network errors (no tracebacks).

## Tests

The offline test suite needs no Spotify/Genius account:

```
python tests/test_main.py
```

## License

MIT, see [LICENSE](LICENSE).
