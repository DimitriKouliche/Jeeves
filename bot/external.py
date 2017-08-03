import requests
import json
from bot import brain

WORDS_API_HOST = "https://wordsapiv1.p.mashape.com/words/"
WORDS_API_KEY = "1sbLJFOyD4mshxPsotSkX2bnoZ3Ep1pO0HgjsnqrMwCsc9YhOr"


def research(word, memory):
    print("Searching the web for word " + word)
    words = []
    headers = {'X-Mashape-Key': WORDS_API_KEY, 'Accept': 'application/json'}
    request = requests.get(WORDS_API_HOST + word, headers=headers)
    content = json.loads(request.content)
    if 'results' in content:
        for data in content['results']:
            words += analyze(data, memory)
    return words


def analyze(data, memory):
    hearing = brain.Hearing()
    raw_words = extract_properties(data, ['typeOf', 'hasParts', 'partOf', 'instanceOf'])
    words = hearing.get_raw_words(raw_words, memory)
    return words


def extract_properties(data, properties):
    key_words = []
    for data_property in properties:
        if data_property in data:
            key_words += data[data_property]
    key_words.append(data['definition'])
    return key_words
