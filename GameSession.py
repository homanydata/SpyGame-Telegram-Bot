from json_handler import choose_word
import random

class GameSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = []
        self.spy = None
        self.word = ''
        self.language = 'english'
    def change_language(self, language):
        self.language = language
    def restart_session(self):
        self.spy = None
        self.players = []
        self.word = ''
    def choose_spy(self):
        self.spy = random.choice(self.players)
    def choose_word(self, dic):
        self.word = choose_word(session=self, data=dic)
