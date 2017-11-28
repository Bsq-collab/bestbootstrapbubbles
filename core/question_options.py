from collections import OrderedDict

from typing import Dict, Iterable, Tuple, Union

from util.annotations import override
from util.namedtuple_factory import register_namedtuple
from util.tupleable import Tupleable

types = OrderedDict((
    ('Multiple Choice', 'multiple'),
    ('True or False', 'boolean'),
))  # type: Dict[str, str]

difficulties = OrderedDict((
    (difficulty.capitalize(), difficulty) for difficulty in ('easy', 'medium', 'hard')
))  # type: Dict[str, str]

categories = OrderedDict((
    ('General Knowledge', 9),
    ('Entertainment, Books', 10),
    ('Entertainment, Film', 11),
    ('Entertainment, Music', 12),
    ('Entertainment, Musicals & Theatres', 13),
    ('Entertainment, Television', 14),
    ('Entertainment, Video Games', 15),
    ('Entertainment, Board Games', 16),
    ('Science & Nature', 17),
    ('Science, Computers', 18),
    ('Science, Mathematics', 19),
    ('Mythology', 20),
    ('Sports', 21),
    ('Geography', 22),
    ('History', 23),
    ('Politics', 24),
    ('Art', 25),
    ('Celebrities', 26),
    ('Animals', 27),
    ('Vehicles', 28),
    ('Entertainment, Comics', 29),
    ('Science, Gadgets', 30),
    ('Entertainment, Japanese Anime & Manga', 31),
    ('Entertainment, Cartoon & Animations', 32),
))  # type: Dict[str, int]

fields = OrderedDict((
    ('type', types),
    ('difficulty', difficulties),
    ('category', categories),
))  # type: Dict[str, Dict[str, Union[str, int]]]


class InvalidQuestionOptionException(Exception):
    pass


@register_namedtuple
class QuestionOptions(Tupleable):
    """
    Question Options POPO.

    :ivar type question type
    :type type str

    :ivar difficulty difficulty of questions
    :type difficulty str

    :ivar category question category
    :type category str
    """
    
    def __init__(self, type, difficulty, category):
        # type: (str, str, str) -> None
        self.type = type
        self.difficulty = difficulty
        self.category = category
    
    @classmethod
    def _make(cls, fields):
        # type: (Iterable[str]) -> QuestionOptions
        return cls(*fields)
    
    @override
    def as_tuple(self):
        # type: () -> Tuple[str, str, str]
        return self.type, self.difficulty, self.category
    
    @classmethod
    def default(cls):
        # type: () -> QuestionOptions
        return cls(None, None, None)
    
    def set_options(self, options):
        # type: (Dict[str, str]) -> None
        """
        Set fields from dict where keys are field names.
        If field value is None or '' or any False coerced value, it's skipped entirely.
        """
        
        # Check if valid options
        for field, converter in fields.viewitems():
            value = options[field]
            if value and value not in converter and value != 'Default':
                raise InvalidQuestionOptionException(
                    '"{}" is not a valid {}.'.format(value, field))
            
        # Now set options for real
        for field in fields:
            value = options[field]
            if value == 'Default':
                value = None
            self.__dict__[field] = value
    
    def _yield_query_string(self):
        # type: () -> Iterable[str]
        """
        Yield name=value query string pairs,
        s.t. a None or '' value is skipped entirely, so default value will be used instead."""
        for field, converter in fields.viewitems():
            value = converter.get(self.__dict__[field], None)
            if value:  # not None or not ''
                yield '{}={}'.format(field, value)
    
    def urlencode(self):
        # type: () -> str
        """Convert to query string."""
        return '&'.join(self._yield_query_string())


def check_fields():
    options = QuestionOptions('', '', '')
    assert all(field in options.__dict__ for field in fields)


# assert that fields in `fields` are same as fields in QuestionOptions
check_fields()

if __name__ == '__main__':
    print QuestionOptions('Multiple Choice', 'Hard', 'General Knowledge').urlencode()
