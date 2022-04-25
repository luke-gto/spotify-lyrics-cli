# spotify-lyrics-cli

Simple Python script to quickly show on the terminal the lyrics of the song that is being currently played on Spotify

1. Create a Python virtual environment to not mess around with your Python installation that's part of your OS. 

2. Install the dependencies with ```pip install -r requirements.txt```

3.  You need to put the credentials for accessing the [Spotify Web API](https://developer.spotify.com/dashboard/login) Spotify Web API and the [Genius API](http://genius.com/api-clients) Genius API in the ```.env``` file:

		SPOTIPY_CLIENT_ID='YOUR CLIENT ID HERE'
		SPOTIPY_CLIENT_SECRET='YOUR CLIENT SECRET HERE'
		SPOTIPY_REDIRECT_URI='YOUR REDIRECT URI HERE'
		GENIUS_TOKEN='YOUR TOKEN HERE'


4. The script is more handy if you can launch it with a [shell alias](https://en.wikipedia.org/wiki/Alias_(command)) alias.