import telebot
from telebot.types import Poll, PollAnswer, User
from lookups import Keys, Messages
import random
from json_handler import choose_word, read_dict
import threading
import GameSession

class SpyGameBot:
    def __init__(self):
        # final attributes
        self.bot = telebot.TeleBot(Keys.TOKEN)
        self.dic = read_dict()
        self.sessions = {}

    def start(self, chat_id):
        session = GameSession(chat_id=chat_id)
        self.sessions[chat_id] = session

        # send poll
        self.bot.send_poll(chat_id=session.chat_id, question=Messages(start_game_prompt,session.language), options=Messages.wonna_play, is_anonymous=False)

    def show_results(self, session):
        self.bot.send_message(chat_id=session.chat_id, text=Messages.show_results(session.spy, session.word))
    
    def start_timer(self, sesion:GameSession):
        def timer_callback():
            self.guessing_time(session)

        # Create a Timer object that runs the callback function after 3 minutes
        timer = threading.Timer(180, timer_callback)  # 180 seconds = 3 minutes
        timer.start()

    def send_private_messages(self, session:GameSession):
        for player in session.players:
            if player != session.spy:
                self.bot.send_message(chat_id=player.id, text=Messages.non_spy_role_assigned(self.word))
            else:
                self.bot.send_message(chat_id=self.spy.id, text=Messages.spy_role_assigned)
    
    def handle_poll(self, pollAnswer: PollAnswer):
        # get group chat id from poll
        group_chat = pollAnswer.poll.chat.id
        
        # differentiate btw participation poll & guessing spy poll
        if self.spy is None:
            # add the voter to the player attribute
            self.players.append(pollAnswer.user)
            
            # check if the poll ended
            if pollAnswer.poll.is_closed:
                # check if players are enough
                if pollAnswer.poll.total_voter_count >= 3:
                    self.spy = random.choice(self.players)
                    self.word = choose_word()
                    # send private msg for each player
                    self.send_private_messages()
                    # start 3 mins timer for questions in the group chat
                    self.start_timer(chat_id=group_chat)

                else:
                    self.bot.send_message(chat_id=group_chat, text=Messages.not_enough_players)
        
        # it is guessing the spy poll
        else:
            # if the poll ended show results
            if pollAnswer.poll.is_closed:
                self.show_results(chat_id=group_chat)

    def guessing_time(self, session:GameSession):
        # send poll to group chat for players to try to guess who is the spy
        options = [f"Player {player.full_name}" for player in session.players]
        self.bot.send_poll(chat_id=session.chat_id, question=Messages.guess_spy, options=options, open_period=60)

    def run(self):
        @self.bot.message_handler(commands=['play'], chat_types=['group'])
        def handle_play_command(message):
            self.start(chat_id=message.chat_id)

        @self.bot.poll_answer_handler()
        def handle_poll_answer(poll_answer):
            self.handle_poll(poll_answer)

        self.bot.polling()

