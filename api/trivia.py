#!usr/bin/python
import requests, json, sqlite3

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

def get_write_data(amount, typing=0, category=0, difficulty=0):
    data = get_questions(amount, typing=0, category=0, difficulty=0)
    db_name = "../data/listen_up.db"
    dab = sqlite3.connect(db_name)
    c = dab.cursor()
    #cmd = "SELECT id FROM Stories ORDER BY id DESC"
    for item in data:
        cmd = "SELECT question FROM questions WHERE question = "+item["question"]
        c.execute(cmd)
        if (cmd!=""):
            print "A clone."
        
    return data



def get_questions(amount, typing=0, category=0, difficulty=0):
    querystr = query_help(amount, typing, category, difficulty)
    #debug print querystr
    source = "https://opentdb.com/api.php?" + querystr
    datastuff = requests.get(source)
    datastuff = datastuff.json()
    results = datastuff["results"]
    return results


'''
query_help will help return a query string for things above 
'''


def query_help(amount, typing, category, difficulty):
    retstring = ""
    typearr = ["", "multiple", "boolean"]
    diffarr = ["", "easy", "medium", "hard"]
    retstring += "amount=" + str(amount)
    if typing != 0: retstring += "&type=" + typearr[typing]
    if category < 9: retstring += "&category=" + str(category)
    if difficulty != 0: retstring += "&difficulty=" + diffarr[difficulty]
    return retstring

get_write_witcha(3,0,9,2)

'''
Corresponding Categories 
 [9, 'General Knowledge']
 [10, 'Entertainment: Books']
 [11, 'Entertainment: Film']
 [12, 'Entertainment: Music']
 [13, 'Entertainment: Musicals & Theatres']
 [14, 'Entertainment: Television']
 [15, 'Entertainment: Video Games']
 [16, 'Entertainment: Board Games']
 [17, 'Science & Nature']
 [18, 'Science: Computers']
 [19, 'Science: Mathematics']
 [20, 'Mythology']
 [21, 'Sports']
 [22, 'Geography']
 [23, 'History']
 [24, 'Politics']
 [25, 'Art']
 [26, 'Celebrities']
 [27, 'Animals']
 [28, 'Vehicles']
 [29, 'Entertainment: Comics']
 [30, 'Science: Gadgets']
 [31, 'Entertainment: Japanese Anime & Manga']
 [32, 'Entertainment: Cartoon & Animations']
'''
