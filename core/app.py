from __future__ import print_function

import os
from sys import stderr

from flask import Flask, Response, flash, render_template, request, session
from typing import Callable, Dict
from werkzeug.datastructures import ImmutableMultiDict

from core import background, question_options
from core.listen_up_db import ListenUpDatabase
from core.question_options import InvalidQuestionOptionException
from core.users import User
from util.flask.flask_utils import form_contains, post_only, preconditions, reroute_to, \
    session_contains
from util.flask.flask_utils_types import Precondition, Router
from util.flask.template_context import add_template_context, context

app = Flask(__name__, template_folder='../templates', static_folder='../static')

db = ListenUpDatabase()

private_sesssion = {}  # type: Dict[int, User]

# Keys in session
UID_KEY = 'uid'


def get_user():
    # type: () -> User
    """Get User in session."""
    return private_sesssion[session[UID_KEY]]


def set_user(user):
    # type: (User) -> None
    """Set/put User in session."""
    session[UID_KEY] = user.id
    private_sesssion[user.id] = user


def remove_user():
    # type: () -> None
    """Remove User from session"""
    del private_sesssion[session[UID_KEY]]
    del session[UID_KEY]


is_logged_in = session_contains(UID_KEY)  # type: Precondition
is_logged_in.func_name = 'is_logged_in'
context[is_logged_in.func_name] = is_logged_in


@app.before_request
def pause_background_threads():
    # type: () -> ()
    """
    Acquire background lock to stop background threads from making any more HTTP requests
    during the Flask request.
    """
    # signal.pthread_kill() doesn't exist in Python 2
    # so can't stop and resume background threads (using SIGSTOP, SIGCONT)
    # that may be in the middle of downloading something
    # so the website might be very slow when downloading stuff
    # because the flask route is being block
    background.lock.acquire()


@app.after_request
def resume_background_threads(response):
    # type: (Response) -> Response
    """Release background lock to allow background threads to continue."""
    # see comment in pause_background_threads()
    background.lock.release()
    return response


@app.reroute_from('/')
@app.route('/welcome')
def welcome():
    # type: () -> Response
    """Render welcome page."""
    return render_template('welcome.html')


def get_user_info():
    # type: () -> (str, str)
    """Get username and password from request.form."""
    form = request.form  # type: ImmutableMultiDict
    return form['username'], form['password']


@app.route('/login')
def login():
    # type: () -> Response
    """Render the login page or reroute to answer_questions if already logged in."""
    if is_logged_in():
        return reroute_to(answer_question)
    return render_template('login.html')


@app.route('/register')
def register():
    # type: () -> Response
    """Render the page for registering a new account."""
    if is_logged_in():
        return reroute_to(answer_question)
    return render_template('signup.html')


@preconditions(login, post_only, form_contains('username', 'password'))
def auth_or_signup(db_user_supplier):
    # type: (Callable[[unicode, unicode], User]) -> Response
    """
    Auth or signup with the username and password in the form
    and given the DB function that gets the user from the DB,
    possibly inserting the new user.
    """
    if is_logged_in():
        reroute_to(answer_question)
    username, password = get_user_info()
    with db:
        try:
            user = db_user_supplier(username, password)
        except db.exception as e:
            e = e  # type: db.exception
            flash(e.message)
            print(e, file=stderr)
            return reroute_to(login)
    set_user(user)
    return reroute_to(answer_question)


@app.route('/signup', methods=['get', 'post'])
def signup():
    # type: () -> Response
    """Add the user to the database and log them in."""
    return auth_or_signup(db.add_user)


"""Precondition decorator rerouting to login if is_logged_in isn't True."""
logged_in = preconditions(login, is_logged_in)  # type: Router


@app.route('/auth', methods=['get', 'post'])
def auth():
    # type: () -> Response
    """
    Authorize and login a User with username and password from POST form.
    If username and password is wrong, flash message raised by db.
    """
    return auth_or_signup(db.get_user)


@app.route('/answer_question')
@logged_in
def answer_question():
    # type: () -> Response
    """Display the user's next question to answer."""
    user = get_user()
    with db:
        if user.has_won():
            return render_template('congrats.html', user=user, song=db.next_song(user, record=True))
        else:
            return render_template('questions.html',
                                   user=user,
                                   question=db.next_question(user),
                                   )


@app.route('/check_answer', methods=['get', 'post'])
@logged_in
@preconditions(answer_question, post_only, form_contains('answer'))
def check_answer():
    # type: () -> Response
    """Check the answer to the question the user has submitted."""
    user = get_user()
    answer = request.form['answer']
    with db:
        question = db.get_question(user.last_question_id)
        if answer != question.answer:
            flash(u'{} is the wrong answer'.format(answer))
        else:
            db.complete_question(user, question)
            print(u'{}\'s points: {}'.format(user.username, user.points))
    return reroute_to(answer_question)


@app.route('/choose_options')
@logged_in
def choose_options():
    # type: () -> Response
    """Render the customize page, where the user can change their question options."""
    return render_template('customize.html',
                           types=question_options.types.viewkeys(),
                           difficulties=question_options.difficulties.viewkeys(),
                           categories=question_options.categories.viewkeys(),
                           )


@app.route('/set_options', methods=['get', 'post'])
@logged_in
@preconditions(choose_options, post_only, form_contains(*question_options.fields.keys()))
def set_options():
    # type: () -> Response
    """Set the user's question options from the form submitted in choose_options()."""
    try:
        get_user().set_options(request.form)
    except InvalidQuestionOptionException as e:
        flash(e.message)
        return reroute_to(choose_options)
    return reroute_to(answer_question)


@app.route('/logout')
@logged_in
def logout():
    # type: () -> Response
    """Log the user out."""
    remove_user()
    return reroute_to(welcome)


def run(debug=True):
    # type: (bool) -> None
    app.debug = True
    app.secret_key = os.urandom(32)
    add_template_context(app)
    # use_named_tuple_json(app)
    app.run()
