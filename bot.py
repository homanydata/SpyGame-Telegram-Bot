import telebot
from telebot.types import Poll
from lookups import Keys, Messages
import random

class SpyGameBot:
    def __init__(self):
        self.bot = telebot.TeleBot(Keys.TOKEN)
        self.players = []
        self.spy = None

    def start_game(self, chat_id):
        # reset attributes from previous turns
        self.players = []
        self.spy = None

        # send poll
        poll = self.bot.send_poll(chat_id=chat_id, question=Messages.start_game_prompt, options=Messages.wonna_play, is_anonymous=False)

    def handle_poll(self, poll: Poll):
        if poll.total_voter_count >= 3 and self.spy is None:
            self.spy = random.choice(poll.options).user.id

            for option in poll.options:
                if option.user.id == self.spy:
                    self.bot.send_message(chat_id=option.user.id, text=Messages.spy_role_assigned)
                else:
                    self.bot.send_message(chat_id=option.user.id, text=Messages.non_spy_role_assigned)
        else:
            self.bot.send_message(chat_id=poll.chat.id, text=Messages.not_enough_players)

        if len(self.players) >= 3 and self.spy is not None:
            self.end_questioning(chat_id=poll.chat.id)

    def end_questioning(self, chat_id):
        options = [f"Player {player}" for player in self.players]
        poll = self.bot.send_poll(chat_id, Messages.guess_spy, options)

    def handle_spy_guess(self, chat_id, options):
        guessed_player_id = options[0].user.id
        if guessed_player_id == self.spy:
            self.bot.send_message(guessed_player_id, Messages.correct_guess)
        else:
            self.bot.send_message(guessed_player_id, Messages.incorrect_guess)

    def run(self):
        @self.bot.message_handler(commands=['play'], chat_types=['group','private'])
        def handle_play_command(message):
            self.start_game(message.chat.id)

        @self.bot.poll_answer_handler()
        def handle_poll_answer(poll_answer):
            # check type of poll (in/out or guessing the spy)
            if poll.question == Messages.guess_spy:
                self.end_questioning(chat_id=poll.chat.id)
                self.handle_spy_guess(chat_id=poll.chat.id, options=poll.options)
            
            # add voters to players attribute
            if poll_answer.user.id not in self.players:
                self.players.append(poll_answer.user.id)
            self.handle_poll(poll_answer.poll)

        self.bot.polling()

