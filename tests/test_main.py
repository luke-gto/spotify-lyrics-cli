"""Offline test suite for spotify-lyrics-cli: python tests/test_main.py

No Spotify or Genius account needed: every network dependency is stubbed.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import main


def run_in_tmp(env_content, argv):
    """Run main.py in a scratch directory (its own .env), return (rc, output)."""
    tmp = Path(tempfile.mkdtemp(prefix="lyrics_test_"))
    try:
        shutil.copy(REPO / "main.py", tmp / "main.py")
        if env_content is not None:
            (tmp / ".env").write_text(env_content)
        proc = subprocess.run(
            [sys.executable, "main.py", *argv],
            capture_output=True,
            text=True,
            cwd=tmp,
        )
        return proc.returncode, proc.stdout + proc.stderr
    finally:
        shutil.rmtree(tmp)


def test_clean_lyrics():
    assert main.clean_lyrics("a\nb\nEmbed") == "a\nb"
    assert main.clean_lyrics("a\nb") == "a\nb"
    assert main.clean_lyrics("a\nEmbedded\n") == "a\nEmbedded"


def test_parser():
    args = main.build_parser().parse_args([])
    assert args.title is None and args.artist is None
    args = main.build_parser().parse_args(["Song", "Artist"])
    assert (args.title, args.artist) == ("Song", "Artist")


def test_half_arguments_rejected():
    try:
        main.main(["Only title"])
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "both a title and an artist" in str(exc)


def test_credentials_missing_env():
    rc, out = run_in_tmp(None, [])
    assert rc == 1 and "No .env file found" in out and "Traceback" not in out


def test_credentials_placeholders():
    rc, out = run_in_tmp((REPO / ".env.example").read_text(), [])
    assert rc == 1 and "Credentials not valid" in out and "Traceback" not in out


def test_credentials_empty_value():
    rc, out = run_in_tmp(
        'SPOTIPY_CLIENT_ID="abc"\nSPOTIPY_CLIENT_SECRET=""\n'
        'SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"\n'
        'GENIUS_TOKEN="xyz"\n',
        [],
    )
    assert rc == 1 and "SPOTIPY_CLIENT_SECRET" in out


def test_credentials_valid():
    rc, out = run_in_tmp(
        'SPOTIPY_CLIENT_ID="0123456789abcdef"\nSPOTIPY_CLIENT_SECRET="s3cr3t"\n'
        'SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"\n'
        'GENIUS_TOKEN="g3nius"\n',
        ["Song", "Artist"],
    )
    # credentials pass; the Genius stub is absent here so the run must fail
    # later with a network/auth error, never on credential validation
    assert "Credentials not valid" not in out and "No .env file found" not in out


def test_get_lyrics_miss():
    class FakeGenius:
        def __init__(self, token):
            pass

        def search_song(self, title, artist):
            return None

    main.lyricsgenius.Genius = FakeGenius
    assert main.get_lyrics("nope", "nobody", "tok") is False


def test_get_lyrics_hit():
    class FakeGenius:
        def __init__(self, token):
            pass

        def search_song(self, title, artist):
            return SimpleNamespace(lyrics="first line\nsecond line\nEmbed")

    main.lyricsgenius.Genius = FakeGenius
    assert main.get_lyrics("s", "a", "tok") is True


def test_spotify_request_error_mapping():
    import spotipy

    def boom():
        raise spotipy.SpotifyOauthError(400, "invalid client", "bad")

    try:
        main.spotify_request("Playback lookup", boom)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "Spotify rejected the credentials" in str(exc)

    assert main.spotify_request("Playback lookup", lambda: 42) == 42


if __name__ == "__main__":
    failures = 0
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            try:
                func()
                print("PASS", name)
            except AssertionError as exc:
                failures += 1
                print("FAIL", name, exc)
    if failures:
        sys.exit("{} test(s) failed".format(failures))
    print("ALL TESTS PASSED")
