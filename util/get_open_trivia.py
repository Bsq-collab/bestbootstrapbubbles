#!usr/bin/python

'''
This will return a list of dictionaries of questions in this format

[{"question":___,"difficulty":___,"category":___,correct_ans":___,"wrong_ans":[__,__,__],"type":___ },]

'''
import urllib2

def get_questions(questions,category):

