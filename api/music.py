import random

import requests
from typing import Tuple


def get_song(num_songs, country, key):
    """Return a song from top `num_songs` of `country` in the form {artist, title, id}."""
    # Filtering songs that are not instrumental, have lyrics,
    # from specified country, are not explicit
    payload = {'apikey': key, 'page': '1', 'page_size': str(num_songs), 'country': country, 'f_has_lyrics': '1', 'f_is_instrumental': '0', 'f_is_explicit': '0'}
    r = requests.get("https://api.musixmatch.com/ws/1.1/chart.tracks.get", params=payload)
    
    # Getting random number between 0 and num_songs - 1
    song = random.randint(0, num_songs - 1)
    
    # Returning track_id of specified songs
    d = r.json()
    ret = d["message"]["body"]["track_list"][song]["track"]

    # Getting clean lyrics
    lyrics = bleeper(get_lyrics(ret["track_id"], key))
    #print "\n\n\nTRACK ID" + str(ret["track_id"]) + "\n\n\n\n"

    # Returning dictionary with artist, title, lyrics, track_id
    return_dict = {'artist' : ret["artist_name"], 'title' : ret["track_name"], 'lyrics' : lyrics, 'track_id' : ret["track_id"]}
    #print bleeper(lyrics)
    
    return return_dict


def get_lyrics(id, key):
    """Get lyrics of a song based on track id (found using `get_song`)."""
    payload = {'apikey': key, 'format': 'json', 'track_id': str(id)}
    r = requests.get("https://api.musixmatch.com/ws/1.1/track.lyrics.get", params=payload)
    d = r.json()
    lyrics = d["message"]["body"]["lyrics"]["lyrics_body"]
    return lyrics

def bleeper(lyrics):
    """Replaces bad words and cleans up lyrics string."""
    '''
    curses = {"fuck" : "heck", "shit" : "shoot", "hell" : "heck", "bitch" : "beep"}
    for word in curses.iterkeys():
        lyrics.lower().replace(word, curses[word])
    '''
    # Lowercase to allow for easier filtering
    lyrics = lyrics.lower()

    # Filtering curses and other bad words
    lyrics = lyrics.replace("fuck", "heck")
    lyrics = lyrics.replace("shit", "shoot")
    lyrics = lyrics.replace("bitch", "beep")
    lyrics = lyrics.replace(" damn", " dang")
    lyrics = lyrics.replace("cocaine", "coca-cola")

    # Removing copyright stuff at end of lyrics
    lyrics = lyrics.replace("...\n\n******* this lyrics is not for commercial use *******\n(1409616514838)", "")

    '''
    # Replace newlines with spaces
    lyrics = lyrics.replace("\n", " ")
    '''
    
    return lyrics

print get_song(5, "us", "7e08dd0d22a97575c80eda84bbfeb353")
#print bleeper(get_lyrics(136765439, '7e08dd0d22a97575c80eda84bbfeb353'))

def random_song(key):
    # type: () -> Tuple[unicode, unicode]
    """Get name and lyrics of a random song."""
    dict = get_song(5, 'us', key)
    name = dict["title"]
    lyrics = dict["lyrics"]
    artist = dict["artist"]
    track_id = dict["track_id"]
    # TODO
    return name, lyrics
