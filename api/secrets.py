import os

import simplejson as json
from typing import Tuple

from util.annotations import override
from util.tupleable import Tupleable
from util.types import Json


class Watson(Tupleable):
    def __init__(self, username, password):
        # type: (str, str) -> None
        self.username = username
        self.password = password
    
    @classmethod
    def from_json(cls, json):
        # type: (Json) -> Watson
        return cls(json['username'], json['password'])
    
    @override
    def as_tuple(self):
        # type: () -> Tuple[str, str]
        return self.username, self.password


class Musix(Tupleable):
    def __init__(self, api_key):
        # type: (str) -> None
        self.api_key = api_key
    
    @classmethod
    def from_json(cls, json):
        # type: (Json) -> Musix
        return cls(json['apikey'])
    
    @override
    def as_tuple(self):
        # type: () -> Tuple[str]
        return self.api_key,


DIRECTIONS = '''
To run Listen Up, you must get API keys for Musixmatch and IBM Watson's Text-to-Speech.
These must be placed in a api/secrets.json file.
Just fill out the blank strings in api/secrets_templates.json with the API keys
and rename it to api/secrets.json.  Then ListenUp will be able to use them correctly.
For more directions on getting the API keys, see the README.md.
'''


def load_secrets(path='api/secrets.json'):
    # type: (str) -> Tuple[Watson, Musix]
    if not os.path.exists(path):
        raise AssertionError(DIRECTIONS)
    with open(path) as f:
        secrets = json.loads(f.read())
    return (
        Watson.from_json(secrets['watson_text_to_speech']),
        Musix.from_json(secrets['musixmatch'])
    )


watson, musix = load_secrets()