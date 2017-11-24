#!usr/bin/python
import requests, json, sqlite3
from HTMLParser import HTMLParser

#Corresponding Categories#
#PLEASE DONT TOUCH IT#
cat = [
 0,0,0,0,0,0,0,0,0,
 [9, 'General Knowledge'],
 [10, 'Entertainment: Books'],
 [11, 'Entertainment: Film'],
 [12, 'Entertainment: Music'],
 [13, 'Entertainment: Musicals & Theatres'],
 [14, 'Entertainment: Television'],
 [15, 'Entertainment: Video Games'],
 [16, 'Entertainment: Board Games'],
 [17, 'Science & Nature'],
 [18, 'Science: Computers'],
 [19, 'Science: Mathematics'],
 [20, 'Mythology'],
 [21, 'Sports'],
 [22, 'Geography'],
 [23, 'History'],
 [24, 'Politics'],
 [25, 'Art'],
 [26, 'Celebrities'],
 [27, 'Animals'],
 [28, 'Vehicles'],
 [29, 'Entertainment: Comics'],
 [30, 'Science: Gadgets'],
 [31, 'Entertainment: Japanese Anime & Manga'],
 [32, 'Entertainment: Cartoon & Animations']
]
typearr = ["", "multiple", "boolean"]
diffarr = ["", "easy", "medium", "hard"]


'''
This will return a list of dictionaries of questions in this format

[{"question":___,"difficulty":___,"category":___,correct_ans":___,"wrong_ans":[__,__,__],"type":___ },]

Guide to arguments:

int amount - amount of questions to request, do not exceed 50.

--The args below are optional--
int typing - 1:multiple, 2:boolean
int category - *see bottom of file for corresponding categories
int difficulty - 1:easy, 2:med, 3:hard
'''

def get_write_witcha(amount, typing=0, category=0, difficulty=0):
    data = get_questions(amount, typing=0, category=0, difficulty=0)
    db_name = "../data/listen_up.db"
    dab = sqlite3.connect(db_name)
    c = dab.cursor()
    for item in data:
        cmd = """SELECT question FROM questions WHERE question = "%s" """%(item["question"])
        c.execute(cmd)
        questionable = c.fetchone()
        if questionable == None:        
            cmd = "SELECT MAX(id) FROM questions"
            c.execute(cmd)
            newID = c.fetchone()[0]
            if newID == None:
            	newID = 0
            else:
            	newID+=1
            	'''
            cmd = "INSERT INTO question values(%i,%s,%s,%s,%i,%i,%s,%s)"%(
            	newID,
            	item["question"],
            	item["correct_answer"],
            	''.join(item["incorrect_answers"]),
            	typing, mult or bool?
            	difficulty, easy, med, hard?
			'''
            print "theres nothing here"
        else:
            print "you screwed up"
    return data



def get_questions(amount, typing=0, category=0, difficulty=0):
    querystr = query_help(amount, typing, category, difficulty)
    source = "https://opentdb.com/api.php?" + querystr
    datastuff = requests.get(source)
    datastuff = datastuff.json()
    #Ew HTML Encoding
    h = HTMLParser()
    results = datastuff["results"]
    for item in results:
        keys = item.keys()
        for key in keys:
            item[key] = h.unescape(item[key])
            try:
                item[key] = item[key].replace("\"","'")
            except(Exception):
                '''
                print item["question"]
                print item["correct_answer"]
                print item["incorrect_answers"]
                '''
                pass
    print results
    return results


'''
query_help will help return a query string for things above 
'''


def query_help(amount, typing, category, difficulty):
    retstring = ""
    retstring += "amount=" + str(amount)
    if typing != 0: retstring += "&type=" + typearr[typing]
    if category < 9: retstring += "&category=" + str(category)
    if difficulty != 0: retstring += "&difficulty=" + diffarr[difficulty]
    return retstring

if __name__ == '__main__':
    get_write_witcha(1,0,9,2)
