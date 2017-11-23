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
        return cls._make(converter.keys()[0] for converter in fields.viewvalues())
    
    def urlencode(self):
        # type: () -> str
        """Convert to query string."""
        return '&'.join(
                '{}={}'.format(field, converter[self.__dict__[field]])
                for field, converter in fields.viewvalues())


def check_fields():
    options = QuestionOptions('', '', '')
    assert all(field in options.__dict__ for field in fields)


# assert that fields in `fields` are same as fields in QuestionOptions
check_fields()
