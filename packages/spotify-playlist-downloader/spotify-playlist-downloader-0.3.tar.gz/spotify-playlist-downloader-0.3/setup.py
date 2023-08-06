from setuptools import setup

setup(
	name = "spotify-playlist-downloader",
	version = "0.3",
	scripts = ["spotify_playlist_downloader"],
        py_modules = ["song", "playlist", "playlists", "auth"]
)
