import requests
from typing import Tuple

from api.secrets import musix
from util.types import Json


def get_song(song_num, country='us', key=musix.api_key):
    # type: (int, str, str) -> Tuple[int, unicode, unicode, unicode]
    """Return the id, artist, song_name, lyrics of the top `song_num`th song."""
    
    # Filtering songs that are not instrumental, have lyrics,
    # from specified country, are not explicit
    payload = {
        'apikey': key,
        'page': song_num,
        'page_size': 1,
        'country': country,
        'f_has_lyrics': '1',
        'f_is_instrumental': '0',
        'f_is_explicit': '0',
    }
    
    response = requests.get('https://api.musixmatch.com/ws/1.1/chart.tracks.get', params=payload) \
        .json()  # type: Json
    
    data = response['message']['body']['track_list'][0]['track']  # type: Json
    id = data['track_id']
    return id, data['artist_name'], data['track_name'], get_lyrics(id, key)


def get_lyrics(id, key=musix.api_key):
    # type: (int, str) -> unicode
    """Get lyrics of a song based on track id (found using `get_song`)."""
    payload = {
        'apikey': key,
        'format': 'json',
        'track_id': id,
    }
    lyrics = requests.get('https://api.musixmatch.com/ws/1.1/track.lyrics.get', params=payload) \
        .json()['message']['body']['lyrics']['lyrics_body']  # type: unicode
    end = lyrics.rfind('*' * 7, 0, lyrics.rfind('*' * 7))
    return lyrics[:end]
