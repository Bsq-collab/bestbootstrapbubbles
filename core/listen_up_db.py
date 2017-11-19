from intbitset import intbitset
from random import randint

from typing import Iterable, List, Tuple, Union

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
            questions BINARY BLOB NOT NULL
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
    
    # User stuff
    
    def get_user(self, username, password):
        # type: (unicode, unicode) -> Union[User, None]
        """
        Get `User` with `username` and `password`.

        If `username` doesn't exist or `password` doesn't match,
        raise an `self.exception` with a message.
        """
        self.db.cursor.execute(
                'SELECT id, password, points, questions FROM users WHERE username = ?',
                [username])
        result = self.db.cursor.fetchone()  # type: Tuple[int, unicode, int, buffer]
        if result is None:
            raise self.exception('username "{}" doesn\'t exist'.format(username))
        user_id, hashed_password, points, questions = result
        if not verify_password(password, hashed_password):
            raise self.exception('wrong password for username "{}"'.format(username))
        return User.from_db(user_id, username, points, questions)
    
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
        questions = intbitset()
        self.db.cursor.execute(
                'INSERT INTO users VALUES (NULL, ?, ?, ?, ?)',
                [username, hash_password(password), points, buffer(questions.fastdump())]
        )
        user_id = self.db.cursor.lastrowid
        self.commit()
        return User(user_id, username, points, questions)
    
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
        self.db.cursor.execute('UPDATE users SET points = ?, questions = ? WHERE id = ?',
                               [user.points, user.serialize_questions(), user.id])
        self.commit()
    
    # Question stuff
    
    def _insert_questions(self, questions):
        # type: (Iterable[Question]) -> None
        self.db.cursor.executemany(
                'INSERT INTO questions VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)',
                (question.serialize_choices().as_tuple() for question in questions)
        )
        self.commit()
    
    def add_questions(self, user, num_questions=None):
        # type: (User, int) -> None
        """Add `num_questions` `Question`s to DB according to `user`'s options."""
        if num_questions is None:
            num_questions = ListenUpDatabase.DEFAULT_BUF_SIZE
        questions = get_questions(user.options, num_questions, self.questions_dir)
        self._insert_questions(questions)
    
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
    # TODO I'm not sure what other stuff I need to do for the songs.
    # TODO How exactly are the songs being selected.
    
    def _insert_song(self, song):
        # type: (Song) -> int
        """Insert `song` into DB and return id."""
        self.db.cursor.execute('INSERT INTO songs VALUES (NULL, ?, ?, ?)', song.as_tuple())
        self.commit()
        return self.db.cursor.lastrowid
    
    def random_song(self):
        # type: () -> Song
        """Get a random `Song` in the DB."""
        num_songs = self.db.max_rowid('songs')
        song_id = randint(1, num_songs)
        self.db.cursor.execute('SELECT name, lyrics, audio_path FROM songs WHERE id = ?', [song_id])
        result = self.db.cursor.fetchone()  # type: Tuple[unicode, unicode, str]
        name, lyrics, audio_path = result
        return Song(song_id, name, lyrics, audio_path)
    
    def new_song(self):
        # type: () -> Song
        """Get a random `Song` not int the DB.  Then insert it."""
        song = Song.random(self.songs_dir)
        song.id = self._insert_song(song)
        return song
