#!usr/bin/python
__authors__ = ['Khyber Sen', 'Bayan Berri', 'Naotaka Kinoshita', 'Brian Leung']
__date__ = '2017-10-30'

from flask import Flask, session, render_template, request, redirect, url_for, flash
from core import app

@app.route("/")
def landing():
	render_template("welcome.jinja2")

if __name__ == '__main__':
    app.debug = True
    app.run()