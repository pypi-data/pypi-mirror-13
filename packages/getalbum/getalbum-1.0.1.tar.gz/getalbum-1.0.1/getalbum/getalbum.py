#!/usr/bin/env python
from __future__ import print_function

import requests

import argparse
import base64
import os
import sys

TOKEN = None


def get_token(id=None, secret=None):
    global TOKEN
    id = os.environ.get("SPOTIFY_CLIENT_ID", None)
    secret = os.environ.get("SPOTIFY_CLIENT_SECRET", None)
    if id and secret and not TOKEN:
        encoded_auth = base64.b64encode(bytes("{}:{}".format(id, secret), 'utf-8'))
        response = requests.post("https://accounts.spotify.com/api/token", data={"grant_type": "client_credentials"}, headers={"Authorization": b"Basic " + encoded_auth}).json()
        TOKEN = response["access_token"] if "access_token" in response else None
    return TOKEN


def get_spotify_api(url, get=False, post=False, data={}, token=None):
    if not token:
        token = get_token()
    h = {"Authorization": "Bearer " + token}
    if not get and not post:
        get = True
    if get:
        return requests.get(url, params=data, headers=h).json()
    elif post:
        return requests.post(url, data=data, headers=h).json


def get_album_tracklist(name, artist=None, token=None):
    """ Get album tracklist. Yields list of track names if successful, otherwise returns None """
    if not token:
        token = get_token()
    album = get_spotify_api("https://api.spotify.com/v1/search", get=True, data={"q": (artist + " - " if artist else "") + name, "type": "album", "limit": 1})
    if album["albums"]["items"]:
        tracks = get_spotify_api(album["albums"]["items"][0]["href"] + "/tracks", get=True)
        output = []
        for track in tracks["items"]:
            output.append([track["artists"][0]["name"], track["name"]])
        return output
    else:
        return "No results"


def main():
    parser = argparse.ArgumentParser(prog="getalbum")
    parser.add_argument("term", help="Search term")
    parser.add_argument("--include-artist", help="Includes artist name in results")
    parser.add_argument("--spotify-id", help="Spotify application client ID")
    parser.add_argument("--spotify-secret", help="Spotify application client secret")
    args = parser.parse_args()
    token = get_token(args.spotify_id, args.spotify_secret)
    if not token:
        print("Could not get credentials. Please set environment variables SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET from https://developer.spotify.com/my-applications/", file=sys.stderr)
        return 1
    for artist, track in get_album_tracklist(args.term, token=token):
        print(("{} - ".format(artist) if args.include_artist else "") + track)
    return 0


if __name__ == "__main__":
    sys.exit(main())
