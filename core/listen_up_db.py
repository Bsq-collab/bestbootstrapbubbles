import random
from intbitset import intbitset
from sqlite3 import IntegrityError

from typing import Iterable, List, Tuple, Union, Set

from core.questions import Question, get_questions
from core.songs import Song
from core.users import User
from util import io
from util.db.db import ApplicationDatabase, ApplicationDatabaseException
from util.password import hash_password, verify_password

SCHEMA = dict(
        users='''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            points INTEGER NOT NULL,
            questions BINARY BLOB NOT NULL,
            songs BINARY BLOB NOT NULL
        )''',
        
        questions='''
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            choices TEXT NOT NULL,
            type INTEGER NOT NULL,
            difficulty INTEGER NOT NULL,
            category TEXT NOT NULL,
            audio_path TEXT NOT NULL
        )''',
        # questions will be a binary python buffer from the intbitset
        
        songs='''
        CREATE TABLE IF NOT EXISTS songs(
            id INTEGER PRIMARY KEY,
            artist TEXT NOT NULL,
            name TEXT NOT NULL,
            lyrics TEXT NOT NULL,
            audio_path TEXT NOT NULL
        )''',
)


class ListenUpDatabaseException(ApplicationDatabaseException):
    pass


# noinspection PyCompatibility
class ListenUpDatabase(ApplicationDatabase):
    """DB wrapper for ListenUp."""
    
    QUESTIONS_DIR = 'trivia'  # type: str
    SONGS_DIR = 'songs'  # type: str
    
    DIRS = [QUESTIONS_DIR, SONGS_DIR]  # type: List[str]
    
    DEFAULT_BUF_SIZE = 10  # type: int
    
    def __init__(self, path='data/listen_up.db', audio_dir='static/audio'):
        # type: (str, str) -> None
        super(ListenUpDatabase, self).__init__(SCHEMA, path, ListenUpDatabaseException)
        self.audio_dir = audio_dir  # type: str
        self.questions_dir = audio_dir + '/' + ListenUpDatabase.QUESTIONS_DIR
        self.songs_dir = audio_dir + '/' + ListenUpDatabase.SONGS_DIR
        for dir_name in ListenUpDatabase.DIRS:
            dir_path = audio_dir + '/' + dir_name
            io.mkdir_if_not_exists(dir_path)
        self._questions = set(self._get_all_questions())  # type: Set[Question]
        self._song_ids = self._get_all_song_ids()  # type: intbitset
    
    def _get_all_questions(self):
        # type: () -> Iterable[Question]
        """Get all questions in DB."""
        for id, question, answer, choices, type, difficulty, category, audio_path \
                in self.db.cursor.execute(
                'SELECT id, question, answer, choices, '
                'type, difficulty, category, audio_path FROM questions'):
            yield Question.from_db(id, question, answer, choices,
                                   type, difficulty, category, audio_path)
    
    def _get_all_song_ids(self):
        # type: () -> intbitset
        """Get all song ids in DB."""
        return intbitset(
                x[0] for x in self.db.cursor.execute('SELECT id FROM songs').fetchall())
    
    # User stuff
    
    def get_user(self, username, password):
        # type: (unicode, unicode) -> Union[User, None]
        """
        Get `User` with `username` and `password`.

        If `username` doesn't exist or `password` doesn't match,
        raise an `self.exception` with a message.
        """
        self.db.cursor.execute(
                'SELECT id, password, points, questions, songs FROM users WHERE username = ?',
                [username])
        result = self.db.cursor.fetchone()  # type: Tuple[int, unicode, int, buffer, buffer]
        if result is None:
            raise self.exception('username "{}" doesn\'t exist'.format(username))
        user_id, hashed_password, points, questions, songs = result
        if not verify_password(password, hashed_password):
            raise self.exception('wrong password for username "{}"'.format(username))
        return User.from_db(user_id, username, points, questions, songs)
    
    def verify_user(self, username, password):
        # type: (unicode, unicode) -> bool
        """Verify `username` and `password` is a valid `User`."""
        return self.get_user(username, password) is not None
    
    def user_exists(self, username):
        # type: (unicode) -> bool
        """Check if User with `username` exists."""
        self.db.cursor.execute('SELECT id FROM users WHERE username = ?', [username])
        return self.db.result_exists()
    
    def _add_user_hard(self, username, password):
        # type: (unicode, unicode) -> User
        points = 0
        empty_buf = buffer(intbitset().fastdump())
        self.db.cursor.execute(
                'INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?)',
                [username, hash_password(password), points, empty_buf, empty_buf]
        )
        user_id = self.db.cursor.lastrowid
        self.commit()
        return User(user_id, username, points, intbitset(), intbitset())
    
    def add_user(self, username, password):
        # type: (unicode, unicode) -> User
        """
        Add and return `User` with `username` and `password`.
        
        If `User` with `username` already exists,
        raise an `self.exception`.
        """
        if self.user_exists(username):
            raise self.exception('username "{}" already exists'.format(username))
        return self._add_user_hard(username, password)
    
    def update_password(self, user, password):
        # type: (User, unicode) -> None
        """Update password to `password` for `user`."""
        self.db.cursor.execute('UPDATE users SET password = ? WHERE id = ?',
                               [hash_password(password), user.id])
        self.commit()
    
    def update_user_stats(self, user):
        # type: (User) -> None
        """Update `user`'s stats in DB according to fields of `user` (not username or password)."""
        self.db.cursor.execute(
                'UPDATE users SET points = ?, questions = ?, songs = ? WHERE id = ?',
                [user.points, user.serialize_questions(), user.serialize_songs(), user.id]
        )
        self.commit()
    
    # Question stuff
    
    def _insert_questions(self, questions):
        # type: (Iterable[Question]) -> None
        # FIXME must ensure that these new questions are unique w.r.t to already inserted questions
        self.db.cursor.executemany(
                'INSERT INTO questions VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)',
                (question.serialize_choices().as_tuple() for question in questions)
        )
        self.commit()
    
    def _get_new_questions(self, user, num_questions):
        # type: (User, int) -> Set[Question]
        """Get exactly `num_questions` new, unique questions."""
        original_questions = list(get_questions(user.options, num_questions, self.questions_dir))
        new_questions = set(original_questions) - self._questions
        self._questions.update(new_questions)
        skipped = len(original_questions) - len(new_questions)
        if skipped > 0:
            new_questions.update(self._get_new_questions(user, skipped))
        return new_questions
    
    def add_questions(self, user, num_questions=None):
        # type: (User, int) -> None
        """Add `num_questions` `Question`s to DB according to `user`'s options."""
        if num_questions is None:
            num_questions = ListenUpDatabase.DEFAULT_BUF_SIZE
        self._insert_questions(self._get_new_questions(user, num_questions))
    
    def get_question(self, question_id):
        # type: (int) -> Question
        """Get `Question` with `question_id`."""
        self.db.cursor.execute(
                'SELECT question, answer, choices, '
                'type, difficulty, category, audio_path '
                'FROM questions WHERE id = ?',
                [question_id]
        )
        result = self.db.cursor.fetchone()  # type: Tuple[unicode, unicode, unicode, unicode, unicode, unicode, str]
        return Question.from_db(*result)
    
    def next_question(self, user):
        # type: (User) -> Question
        """Get next `Question` for `user` that `user` hasn't answered before."""
        question_ids = user.questions  # type: intbitset
        # TODO will this work if no rows in table yet?
        max_question_id = self.db.max_rowid('questions')  # type: int
        # filtering possible question ids using fast intbitset in Python,
        # rather than running a complicated and slow SQL query.
        # will be performant if question_ids are dense, meaning few deleted questions
        question_id = next(
                (id for id in xrange(1, max_question_id + 1) if
                 id not in question_ids))  # type: int
        if question_id is None:  # if there are no new questions left
            self.add_questions(user)
            question_id = max_question_id + 1
        return self.get_question(question_id)
    
    def complete_question(self, user, question):
        # type: (User, Question) -> None
        """Complete `question` for the `user`, incrementing their points and questions."""
        user.complete_question(question)
        self.update_user_stats(user)
    
    # Song stuff
    
    def _insert_song(self, song):
        # type: (Song) -> bool
        """Insert `song` into DB and return true if it is a new, unique song and was inserted."""
        try:
            self.db.cursor.execute('INSERT INTO songs VALUES (?, ?, ?, ?)', song.as_tuple())
        except IntegrityError:
            return False
        self.commit()
        return True
    
    def next_song(self, user, record=True):
        # type: (User, bool) -> Song
        """
        Get the next random `Song` in the DB that `user` hasn't heard yet.
        If `record`, call play_song() for the song and `user`.
        """
        new_song_ids = self._song_ids & user.songs
        song_id = new_song_ids[random.randrange(0, len(new_song_ids))]
        self.db.cursor.execute(
                'SELECT name, artist, lyrics, audio_path FROM songs '
                'LIMIT 1 ORDER BY RANDOM()'
        )
        result = self.db.cursor.fetchone()  # type: Tuple[unicode, unicode, unicode, str]
        name, artist, lyrics, audio_path = result
        song = Song(song_id, artist, name, lyrics, audio_path)
        if record:
            self.play_song(user, song)
        return song
    
    def new_song(self):
        # type: () -> Song
        """Get a random `Song` not int the DB.  Then insert it."""
        # Keep getting new random songs until a new one is found.
        while True:
            song = Song.random(self.songs_dir)
            if self._insert_song(song):
                return song
    
    def play_song(self, user, song):
        # type: (User, Song) -> None
        """Record that `song` was played for `user` by adding to `user`'s questions."""
        user.play_song(song)
        self.update_user_stats(user)
