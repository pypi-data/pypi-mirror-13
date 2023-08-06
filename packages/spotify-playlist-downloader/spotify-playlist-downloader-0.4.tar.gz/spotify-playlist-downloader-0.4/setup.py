from setuptools import setup

setup(
	name = "spotify-playlist-downloader",
	version = "0.4",
	scripts = ["spotify_playlist_downloader"],
        py_modules = ["song", "playlist", "playlists", "auth"],
        install_requires = ["requests"]
)
