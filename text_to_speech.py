# coding: utf-8
from __future__ import print_function
import simplejson as json
from watson_developer_cloud import TextToSpeechV1 as TextToSpeech
from core.secrets import watson
text_to_speech = TextToSpeech(username=watson.username, password=watson.password)
with open('hello_world.wav') as f:
    
    
    f.close()
    
with open('hello_world.wav', 'wb') as f:
    f.write(text_to_speech.synthesize('Hello, World!', accept='audio/wav', voice='en-US_AllisonVoice'))
    
print(json.dumps(text_to_speech.pronunciation('Watson', pronunciation_format='spr'), indent=4))
import requests
questions = requests.get('https://opentdb.com/api.php?amount=10').json()
questions
text = '.\n'.join(question['question'] for question in questions['results'])
text
import urllib2
text = urllib2.unquote(text).decode('utf-8')
text
with open('hello_world.wav', 'wb') as f:
    f.write(text_to_speech.synthesize(text, accept='audio/wav', voice='en-US_AllisonVoice'))
    
get_ipython().magic(u'save ')
