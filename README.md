# bestbootstrapbubbles
## Bayan Berri, Naotaka Kinoshita, Brian Leung, Khyber Sen

### Overview:
Listen Up is a game which uses the Watson Text to Speech API, Open_Trivia API, and Musixmatch API. In order to play the game a user must:
1. Login or register (depending on if they have an account)
2. Answer at least five questions correctly in order to customize the types of questions they get.
3. After answering five questions correctly a random song will play from Musix Match.
4. Now the user can customize the types of questions and difficulty and play again. 

### Instructions on getting API Keys and Running:

#### How to procure API Keys

First make a copy of 'secrets_template.json' named 'secrets.json' in the api directory.

* ##### Watson Text to Speech

    1. Go to [Watson Text to Speech](https://www.ibm.com/watson/services/text-to-speech/).
    2. Click 'Get started free'.
    3. Fill out the form to create an account.
    4. Open the link in the email sent by The Bluemix Team to activate your account.
    5. Sign into your new account.
    6. You should now be at [https://console.bluemix.net/catalog/services/text-to-speech/](https://console.bluemix.net/catalog/services/text-to-speech/).
        If not, click on that link.
    7. Click 'Create'.
    8. Click on 'Service Credentials'.
    9. Click on 'New credential' and then 'Add' in the pop-up to create your credentials.
    10. Click 'View credentials' in the new credential that just appeared.
    11. Copy the username and password into the fields under 'watson_text_to_speech' in 'secrets.json'.

* ##### Open_Trivia

    No API keys needed

* ##### Musixmatch

    1. 

### Dependencies and how to install them
These are listed in requirements.txt:
* typing
* flask
* requests
* watson_developer_cloud
* intbitset
* simplejson
* passlib

We suggest using a virtual environment

In order to install all dependencies, run this line:

` $ pip install -r requirements.txt `

### How to run Listen Up

After installing the dependencies, run:
 
`$ python app.py`

Then, in a browser, go to the website at [http://localhost:5000/](http://localhost:5000/) and follow the directions.