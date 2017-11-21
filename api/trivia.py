#!usr/bin/python
import urllib2, json

#from typing import Dict, Any, Iterable

# def get_questions(options, num_questions):
    # type: (Dict[str, Any], int) -> Dict[str, Any]
    # """Download JSON of `num_questions` questions with `options`."""
    # TODO
    # pass


'''
This will return a list of dictionaries of questions in this format

[{"question":___,"difficulty":___,"category":___,correct_ans":___,"wrong_ans":[__,__,__],"type":___ },]

Guide to arguments:

int amount - amount of questions to request, do not exceed 50
int typing - 1:multiple, 2:boolean
int category - *see json list of all categories, in the opentrivia documentation
int difficulty - 1:easy, 2:med, 3:hard
'''
def get_questions(amount,typing=0,category=0,difficulty=0):
	source = "https://opentdb.com/api.php?"+query_help(amount,typing,category,difficulty)
	datastuff = urllib2.urlopen(source)
	jason = datastuff.read()
	d = json.loads(jason)
	results = d["results"]
	#ignore
	target = []
	for item in results:
		tempdict = {}
		tempdict["question"]
	return results

'''
This will help return a query string 
'''
def query_help(amount,typing,category,difficulty):
	retstring = ""
	typearr = ["","multiple","boolean"]
	diffarr = ["","easy","medium","hard"]
	retstring+="amount="+str(amount)
	if typing!=0: retstring+="&type="+typearr[typing]
	if category<9: retstring+="&category="+str(category)
	if difficulty!=0: retstring+="&difficulty="+diffarr[difficulty]
	return retstring