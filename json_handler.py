from lookups import Keys
import random
import json

def read_dict():
    with open(Keys.File_Directory, 'r') as json_file:
        data = json.load(json_file)
    return data

def choose_word(data: dict, session):
    thisData = data[session.language]
    theme = random.choice(list(thisData.keys()))
    word = random.choice(thisData[theme])
    return word
