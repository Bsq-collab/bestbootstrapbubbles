from typing import Any, Iterable, Tuple

from api import music
from api.text_to_speech import AudioDownloader
from util import io
from util.annotations import override
from util.namedtuple_factory import register_namedtuple
from util.tupleable import Tupleable


@register_namedtuple
class Song(Tupleable, AudioDownloader):
    """
    Song POPO.
    
    :ivar id DB id
    :type id int
    
    :ivar name name of song
    :type name unicode
    
    :ivar lyrics lyrics of song
    :type lyrics unicode
    
    :ivar audio_path path to audio file that reads the lyrics aloud
        will be a str normally, but None when the audio hasn't been downloaded yet
    :type audio_path str
    """
    
    def __init__(self, id, name, lyrics, audio_path=None):
        # type: (int, unicode, unicode, str) -> None
        self.id = id
        self.name = name
        self.lyrics = lyrics
        self.audio_path = audio_path
    
    @classmethod
    def _make(cls, fields):
        # type: (Iterable[Any]) -> Song
        return cls(*fields)
    
    def as_tuple(self):
        # type: () -> Tuple[int, unicode, unicode, str]
        return self.id, self.name, self.lyrics, self.audio_path
    
    @classmethod
    def random(cls, dir_path):
        # type: (str) -> Song
        """Create a random Song."""
        name, lyrics = music.random_song()
        song = cls(None, name, lyrics)
        song.download_audio(dir_path)
        return song
    
    @override
    def filename(self):
        # type: () -> str
        """Create filename used for saving audio file."""
        return '{}. {}'.format(self.id, io.sanitize_filename(self.name))
    
    def bleeped_lyrics(self):
        # type: () -> unicode
        """Replaces bad words and cleans up lyrics string."""
    
        replacements = {
            'fuck': 'heck',
            'shit': 'shoot',
            'bitch': 'beep',
            'damn': 'dang',
            'cocaine': 'coca-cola',
            '...\n\n******* this lyrics is not for commercial use *******\n(1409616514838)': '',
            '\n': ' '
        }
    
        lyrics = self.lyrics.lower()
        for replacing, replacement in replacements.viewvalues():
            lyrics = lyrics.replace(replacing, replacement)
        return lyrics
    
    @override
    def text(self):
        # type: () -> unicode
        """Convert entire question to text Watson will read."""
        return self.bleeped_lyrics()
