import random

import requests


def get_song(num_songs, country, key):
    """Return a song from top `num_songs` of `country` in the form {artist, title, id}."""
    # Filtering songs that are not instrumental, have lyrics,
    # from specified country, are not explicit
    payload = {'apikey': key, 'page': '1', 'page_size': str(num_songs), 'country': country,
               'f_has_lyrics': '1', 'f_is_instrumental': '0', 'f_is_explicit': '0'}
    r = requests.get("https://api.musixmatch.com/ws/1.1/chart.tracks.get", params=payload)
    
    # Getting random number between 0 and num_songs - 1
    song = random.randint(0, num_songs - 1)
    
    # Returning track_id of specified songs
    d = r.json()
    ret = d["message"]["body"]["track_list"][song]["track"]
    return_dict = {'artist': ret["artist_name"], 'title': ret["track_name"], 'id': ret["track_id"]}
    return return_dict


def get_lyrics(id, key):
    """Get lyrics of a song based on track id (found using `get_song`)."""
    payload = {'apikey': key, 'format': 'json', 'track_id': str(id)}
    r = requests.get("https://api.musixmatch.com/ws/1.1/track.lyrics.get", params=payload)
    d = r.json()
    lyrics = d["message"]["body"]["lyrics"]["lyrics_body"]
    return lyrics
