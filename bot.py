import telebot
from telebot.types import Poll, PollAnswer, User
from lookups import Keys, Messages, Timer
import random
from json_handler import choose_word, read_dict
import threading
from GameSession import GameSession

class SpyGameBot:
    def __init__(self):
        self.bot = telebot.TeleBot(Keys.TOKEN)
        self.dic = read_dict()
        self.sessions = {}
        self.poll_chat_ids = {}

    def start(self, chat_id):
        session = GameSession(chat_id)
        self.sessions[chat_id] = session

        # send poll
        sent_message = self.bot.send_poll(chat_id=session.chat_id, question=Messages.start_game_prompt(session.language), options=[Messages.wonna_play(language=session.language)]*2, is_anonymous=False)
        poll = sent_message.poll
        
        # map this poll_id to its chat_id
        self.poll_chat_ids[poll.id] = chat_id
        
        def check_enough_players():
            if poll.total_voter_count >= 3:
                    session.spy = random.choice(session.players)
                    session.word = choose_word()
                    # send private msg for each player
                    self.send_private_messages(session=session)
                    # start timer for questions in the group chat
                    self.start_timer(chat_id=chat_id)
            else:
                self.bot.send_message(chat_id=chat_id, text=Messages.no_enough_players(language=session.language))
        
        timer = threading.Timer(Timer.waiting_players, check_enough_players)
        timer.start()

    def show_results(self, session):
        self.bot.send_message(chat_id=session.chat_id, text=Messages.show_results(spy=session.spy, word=session.word,language=session.language))

    def start_timer(self, session:GameSession):
        def timer_callback(session):
            self.guessing_time(session)

        # Create a Timer object that runs the callback function after 3 minutes
        timer = threading.Timer(Timer.questions_time, timer_callback, session=session)  # 180 seconds = 3 minutes
        timer.start()

    def send_private_messages(self, session:GameSession):
        for player in session.players:
            if player != session.spy:
                self.bot.send_message(chat_id=player.id, text=Messages.send_word(word=session.word,language=session.language))
            else:
                self.bot.send_message(chat_id=self.spy.id, text=Messages.spy_role_assigned(language=session.language))
    
    def handle_poll_answer(self, pollAnswer: PollAnswer):
        # get group chat id from poll
        group_chat = self.poll_chat_ids[pollAnswer.poll_id]
        session = self.sessions[group_chat]
        
        # differentiate btw participation poll & guessing spy poll
        if session.spy is None:
            # add the voter to the player attribute
            session.players.append(pollAnswer.user)
            
            # # check if the poll ended
            # if pollAnswer.poll.is_closed:
            #     # check if players are enough
            #     if poll.total_voter_count >= 3:
            #         session.spy = random.choice(session.players)
            #         session.word = choose_word()
            #         # send private msg for each player
            #         self.send_private_messages()
            #         # start 3 mins timer for questions in the group chat
            #         self.start_timer(chat_id=group_chat)

            #     else:
            #         self.bot.send_message(chat_id=group_chat, text=Messages.no_enough_players(language=session.language))
        
        # it is guessing the spy poll
        else:
            # if the poll ended show results
            if pollAnswer.poll.is_closed:
                self.show_results(chat_id=group_chat)

    def guessing_time(self, session:GameSession):
        # send poll to group chat for players to try to guess who is the spy
        options = [f"Player {player.full_name}" for player in session.players]
        self.bot.send_poll(chat_id=session.chat_id, question=Messages.guess_spy(), options=options, open_period=60)

    def run(self):
        @self.bot.message_handler(commands=['play'], chat_types=['group'])
        def handle_play_command(message):
            self.start(chat_id=message.chat.id)
        
        @self.bot.message_handler(func=lambda message:True, chat_types=['private'])
        def repeat(message):
            self.bot.send_message(chat_id=message.chat.id, text="hello")

        @self.bot.poll_answer_handler()
        def handle_answer(poll_answer):
            self.handle_poll_answer(poll_answer)

        self.bot.polling()

