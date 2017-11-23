import requests
from typing import Tuple

from api.secrets import musix
from util.types import Json


def get_song(num_songs, song, country, key=musix.api_key):
    # type: (int, str, str, str) -> Tuple[int, unicode, unicode, unicode]
    """Return a song #`song` from top `num_songs` of `country` in the form {artist, title, id}."""
    
    # Filtering songs that are not instrumental, have lyrics,
    # from specified country, are not explicit
    payload = {
        'apikey': key,
        'page': '1',
        'page_size': str(num_songs),
        'country': country,
        'f_has_lyrics': '1',
        'f_is_instrumental': '0',
        'f_is_explicit': '0',
    }
    
    data = requests.get('https://api.musixmatch.com/ws/1.1/chart.tracks.get', params=payload)\
        .json()['message']['body']['track_list'][song]['track']  # type: Json
    id = data['track_id']
    return id, data['artist_name'], data['track_name'], get_lyrics(id, key)


def get_lyrics(id, key=musix.api_key):
    # type: (int, str) -> unicode
    """Get lyrics of a song based on track id (found using `get_song`)."""
    payload = {
        'apikey': key,
        'format': 'json',
        'track_id': str(id),
    }
    return requests.get('https://api.musixmatch.com/ws/1.1/track.lyrics.get', params=payload) \
        .json()['message']['body']['lyrics']['lyrics_body']


# print get_song(5, "us", 1, 'INSERT_KEY_HERE')
# print bleeper(get_lyrics(136765439, 'INSERT_KEY_HERE'))

def random_song(key=musix.api_key):
    # type: () -> Tuple[int, unicode, unicode, unicode]
    """Get name and lyrics of a random song."""
    return get_song(5, 'us', key)
