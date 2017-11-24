from watson_developer_cloud import TextToSpeechV1 as TextToSpeech

from api.secrets import watson

text_to_speech = TextToSpeech(username=watson.username, password=watson.password)


def download_audio(text, path, encoding='wav', voice='en-US_AllisonVoice'):
    # type: (unicode, str) -> None
    """Download `text` to filename `path`."""
    with open(path, 'wb') as f:
        f.write(text_to_speech.synthesize(text, accept='audio/' + encoding, voice=voice))


class AudioDownloader(object):
    """Abstract mixin with download_audio() method using filename() and text() abstract methods."""

    def __init__(self, audio_path):
        # type: (str) -> None
        self.audio_path = audio_path

    def filename(self):
        # type: () -> str
        """Create filename used for saving audio file."""
        pass
    
    def text(self):
        # type: () -> unicode
        """Convert entire object to text Watson will read."""
        pass
    
    def download_audio(self, dir_path, encoding='wav'):
        # type: (str) -> None
        """Download audio in `dir_path`."""
        filename = self.filename()
        path = dir_path + '/' + filename + '.' + encoding
        download_audio(self.text(), path, encoding=encoding)
        self.audio_path = path