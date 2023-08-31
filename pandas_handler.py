import pandas as pd
from lookups import Keys
import random
import json

def read_dict():
    with open(Keys.File_Directory, 'r') as json_file:
        data = json.load(json_file)
    return data

def choose_word(data: dict):
    theme = random.choice(list(data.keys()))
    word = random.choice(data[theme])
    return word
