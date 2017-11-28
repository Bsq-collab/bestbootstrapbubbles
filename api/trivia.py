from HTMLParser import HTMLParser

import requests
from typing import Iterable, List

from core.question_options import QuestionOptions
from util.types import Json

html_parser = HTMLParser()


def get_questions(num_questions, options):
    # type: (int, QuestionOptions) -> Iterable[Json]
    url = 'https://opentdb.com/api.php?amount={}&{}'.format(num_questions, options.urlencode())
    results = requests.get(url).json()['results']  # type: List[Json]
    for result in results:
        result['question'] = html_parser.unescape(result['question'])
        result['correct_answer'] = html_parser.unescape(result['correct_answer'])
        result['incorrect_answers'] = \
            [html_parser.unescape(answer) for answer in result['incorrect_answers']]
    return results
