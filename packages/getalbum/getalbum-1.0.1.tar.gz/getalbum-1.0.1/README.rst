getalbum
========

Get album track list from Spotify

Usage
-----

::

    usage: getalbum [-h] [--artist ARTIST] [--spotify-id SPOTIFY_ID]
                    [--spotify-secret SPOTIFY_SECRET]
                    album

    positional arguments:
      album                 Specify album name

    optional arguments:
      -h, --help            show this help message and exit
      --artist ARTIST       Specify artist name
      --spotify-id SPOTIFY_ID
                            Spotify application client ID
      --spotify-secret SPOTIFY_SECRET
                            Spotify application client secret

Installation
------------

Via ``pip``:

::

    pip3 install getalbum

Alternatively:

-  Clone the repository, ``cd getalbum``
-  Run ``python3 setup.py install`` or ``pip3 install -e``
