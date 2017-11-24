from __future__ import print_function

import os
from sys import stderr

from flask import Flask, Response, flash, render_template, request, session
from typing import Callable
from werkzeug.datastructures import ImmutableMultiDict

from core import question_options
from core.listen_up_db import ListenUpDatabase
from core.users import User
from util.flask.flask_json import use_named_tuple_json
from util.flask.flask_utils import form_contains, post_only, preconditions, reroute_to, \
    session_contains
from util.flask.flask_utils_types import Precondition, Router
from util.flask.template_context import add_template_context

app = Flask(__name__)

db = ListenUpDatabase()

# Keys in session
USER_KEY = 'user'


def get_user():
    # type: () -> User
    """Get User in session."""
    return session[USER_KEY]


is_logged_in = session_contains(USER_KEY)  # type: Precondition
is_logged_in.func_name = 'is_logged_in'


@app.reroute_from('/')
@app.route('/welcome')
def welcome():
    # type: () -> Response
    return render_template('welcome.jinja2', is_loggin_in=is_logged_in())


def get_user_info():
    # type: () -> (str, str)
    """Get username and password from request.form."""
    form = request.form  # type: ImmutableMultiDict
    return form['username'], form['password']


@app.route('/login')
def login():
    # type: () -> Response
    if is_logged_in():
        return reroute_to(answer_question)
    return render_template('login.jinja2')


@preconditions(login, post_only, form_contains('username', 'password'))
def auth_or_signup(db_user_supplier):
    # type: (Callable[[unicode, unicode], User]) -> Response
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
    
    session[USER_KEY] = user
    return reroute_to(answer_question)


@app.route('/signup', methods=['get', 'post'])
def signup():
    # type: () -> Response
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
    """Display a User's home page with all of his edited and unedited Stories."""
    user = get_user()
    if user.has_won():
        return render_template('congrats.jinja2', user=user, song=db.next_song(user, record=True))
    else:
        with db:
            return render_template('questions.jinja2',
                                   user=user,
                                   question=db.next_question(user),
                                   )


@app.route('/check_question', methods=['get', 'post'])
@logged_in
@preconditions(answer_question, post_only, form_contains('answer'))
def check_question():
    # type: () -> Response
    user = get_user()
    answer = request.form['answer']
    with db:
        question = db.get_question(user.last_question_id)
        if answer != question.answer:
            # TODO
            pass
        else:
            db.complete_question(user, question)
    return reroute_to(answer_question)


@app.route('/choose_options')
@logged_in
def choose_options():
    # type: () -> Response
    return render_template('choose_options.jinja2',
                           types=question_options.types.viewkeys(),
                           difficulties=question_options.difficulties.viewkeys(),
                           categories=question_options.categories.viewkeys(),
                           )


@app.route('/set_options', methods=['get', 'post'])
@logged_in
@preconditions(choose_options, post_only, form_contains(*question_options.fields.keys()))
def set_options():
    # type: () -> Response
    get_user().set_options(request.form)
    return reroute_to(answer_question)


@app.route('/logout')
def logout():
    # type: () -> Response
    del session[USER_KEY]
    return reroute_to(welcome)


def run(debug=True):
    # type: (bool) -> None
    app.debug = True
    app.secret_key = os.urandom(32)
    add_template_context(app)
    use_named_tuple_json(app)
    app.run()
