import simplejson as json
from typing import Any, Dict, Iterable, List, Tuple

from api import text_to_speech, trivia
from api.text_to_speech import AudioDownloader
from util.annotations import override
from util.namedtuple_factory import register_namedtuple


@register_namedtuple
class Question(AudioDownloader):
    """
    Trivia question POPO.
    
    :ivar id DB id
    :type id int
    
    :ivar question question
    :type question unicode
    
    :ivar answer correct answer to question
    :type answer unicode
    
    :ivar choices all possible answers, including correct and incorrect answers
        will be a list normally, but pure unicode upon (JSON) serialization
    :type choices Union[List[unicode], unicode]
    
    :ivar type multiple (multiple choice) or boolean (true or false)
    :type type unicode
    
    :ivar difficulty easy, medium, or hard
    :type difficulty unicode
    
    :ivar category category of question
    :type category unicode
    
    :ivar audio_path path to audio file that reads the question and choices aloud
        will be a str normally, but None when the audio hasn't been downloaded yet
    :type audio_path str
    """
    
    def __init__(self, id, question, answer, choices, type, difficulty, category, audio_path=None):
        # type: (int, unicode, unicode, List[unicode], unicode, unicode, unicode, str) -> None
        self.id = id
        self.question = question
        self.answer = answer
        self.choices = choices
        self.type = type
        self.difficulty = difficulty
        self.category = category
        self.audio_path = audio_path
    
    @classmethod
    def _make(cls, fields):
        # type: (Iterable[Any]) -> Question
        return cls(*fields)
    
    def as_tuple(self):
        # type: () -> Tuple[int, unicode, unicode, List[unicode], unicode, unicode, unicode, str]
        return self.id, self.question, self.answer, self.choices, \
               self.type, self.difficulty, self.category, self.audio_path
    
    @classmethod
    def from_db(cls, id, question, answer, choices_json, type, difficulty, category, audio_path):
        # type: (int, unicode, unicode, unicode, unicode, unicode, unicode, str) -> Question
        choices = list(json.loads(choices_json))  # type: List[unicode]
        return cls(id, question, answer, choices, type, difficulty, category, audio_path)
    
    @classmethod
    def from_json(cls, json):
        # type: (Dict[str, Any]) -> Question
        """Create Question from JSON from trivia.py."""
        answer = json['answer']
        choices = [answer]
        choices.extend(json['incorrect_answers'])  # FIXME might be wrong field name
        return cls(
                id=None,
                question=json['question'],
                answer=answer,
                choices=choices,
                type=json['type'],
                difficulty=json['difficulty'],
                category=json['category'],
        )
    
    @override
    def filename(self):
        # type: () -> str
        """Create filename used for saving audio file."""
        # TODO
        pass
    
    @override
    def text(self):
        # type: () -> unicode
        """Convert entire question to text Watson will read."""
        # TODO
        pass
    
    def serialize_choices(self):
        # type: () -> Question
        """
        Serialize (JSONify) choices list to insert into SQLite DB.
        Return self for chaining.
        """
        # noinspection PyAttributeOutsideInit
        self.choices = json.dumps(self.choices)
        return self
    
    def __repr__(self):
        return 'Question(%s, %s, %s, %s, %s, %s, %s, %s)' % self.as_tuple()


def get_questions(options, num_questions, dir_path):
    # type: (Dict[str, Any], int, str) -> Iterable[Question]
    """Download and return `num_questions` Questions with `options` into `dir_path`."""
    questions_json = trivia.get_questions(options, num_questions)  # type: Iterable[Dict[str, Any]]
    for question_json in questions_json:
        question = Question.from_json(question_json)
        question.download_audio(dir_path)
        yield question
