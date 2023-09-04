from lookups import Keys
import random
import json

def read_dict():
    with open(Keys.File_Directory, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def choose_word(data: dict, session):
    thisData = data[session.language]
    theme = random.choice(list(thisData.keys()))
    word = random.choice(thisData[theme])
    return word

def choose_word_randomly(data:dict, session):
    data = data[session.language]
    all_words = []
    # merge all words from all themes into one big list, all_words list
    for theme, words in data.items():
        all_words.extend(words)
    
    word = random.choice(all_words)
    return word
