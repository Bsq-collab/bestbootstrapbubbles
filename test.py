from __future__ import print_function

from core.listen_up_db import ListenUpDatabase, ListenUpDatabaseException
from core.questions import Question

if __name__ == '__main__':
    db = ListenUpDatabase()
    with db:
        db.clear()
        try:
            db.add_user(u'Khyber', u'Sen')
        except db.exception as e:
            print(e.message)
        print(db.user_exists(u'Khyber'))
        user = db.get_user(u'Khyber', u'Sen')
        print(user)
        # db.complete_question(user, Question(1, None, None, None, None, None, None, None))
        print(user)
        
        # song = db.new_song()
        # print(song)
