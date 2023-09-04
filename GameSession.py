from json_handler import choose_word, choose_word_randomly
import random
from lookups import Keys

class GameSession:
    def __init__(self, chat_id):
        # when a session is created, initiate attributes
        self.chat_id = chat_id
        # set language to default
        self.language = Keys.Default_Language
        # session temporary attributes for each turn: players, spy, word
        self.restart_session()
    def change_language(self, language):
        self.language = language
    def restart_session(self):
        self.spy = None
        self.players = []
        self.word = ''
    def choose_spy(self):
        # randomly choose a spy from the players
        self.spy = random.choice(self.players)
    def choose_word(self, dic):
        # choose a word from the dictionary of words
        self.word = choose_word_randomly(session=self, data=dic)
    def players_options(self):
        # a list for guessing spy poll
        options = [f"Player {player.full_name}" for player in self.players]
        return options
    def __str__(self) -> str:
        return "("+ str(self.chat_id) + "," + self.language+")"
