import telebot
from telebot.types import Poll, PollAnswer, User
from telebot import types
from lookups import Keys, Messages, Timer, Errors, Markups
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
        try:
            self.sessions[chat_id].restart_session()
        except:
            session = GameSession(chat_id)
            self.sessions[chat_id] = session

        # send poll
        sent_message = self.bot.send_poll(chat_id=session.chat_id, question=Messages.start_game_prompt(session.language), options=[Messages.wonna_play(language=session.language)]*2, is_anonymous=False)
        poll = sent_message.poll
        
        # map this poll_id to its chat_id
        self.poll_chat_ids[poll.id] = chat_id
        # wait till users join the game and vote
        self.start_timer(session=session, time=Timer.waiting_players, function=self.check_enough_players, poll=poll, session=session)

    def check_enough_players(self, poll, session):
            if poll.total_voter_count >= 3:
                    session.spy = random.choice(session.players)
                    session.word = choose_word()
                    # send private msg for each player
                    self.send_private_messages(session=session)
                    # start timer for questions in the group chat
                    self.start_timer(session=session, time=Timer.questions_time, function=self.guessing_time(session=session))
            else:
                self.bot.send_message(chat_id=session.chat_id, text=Messages.no_enough_players(language=session.language))

    def show_results(self, session):
        self.bot.send_message(chat_id=session.chat_id, text=Messages.show_results(spy=session.spy, word=session.word,language=session.language))

    def start_timer(self, session:GameSession, function, time):
        # Create a Timer object that runs the callback function after 3 minutes
        timer = threading.Timer(interval=time, function=function, session=session)
        timer.start()

    def send_private_messages(self, session:GameSession):
        for player in session.players:
            try:
                if player != session.spy:
                    self.bot.send_message(chat_id=player.id, text=Messages.send_word(word=session.word,language=session.language))
                else:
                    self.bot.send_message(chat_id=self.spy.id, text=Messages.spy_role_assigned(language=session.language))
            except:
                self.bot.send_message(chat_id=session.chat_id, text=Errors.newUserError(language=session.language))
    
    def handle_poll_answer(self, pollAnswer: PollAnswer):
        # get group chat id from poll
        group_chat = self.poll_chat_ids[pollAnswer.poll_id]
        session = self.sessions[group_chat]
        
        # only if poll is participation poll
        if session.spy is None:
            # add the voter to the player attribute
            session.players.append(pollAnswer.user)

    def guessing_time(self, session:GameSession):
        # send poll to group chat for players to try to guess who is the spy
        options = [f"Player {player.full_name}" for player in session.players]
        self.bot.send_poll(chat_id=session.chat_id, question=Messages.guess_spy(language=session.language), options=options, open_period=60)
        # start timer for poll time until results shown
        self.start_timer(session=session, time=Timer.guessing_spy, function=self.show_results(session=session))

    def run(self):
        # this is the actual main body of the bot, other functions are helpers
        @self.bot.message_handler(commands=['play'], chat_types=['group'])
        def handle_play_command(message):
            self.start(chat_id=message.chat.id)
        
        @self.bot.message_handler(commands=['change_language'], chat_types=['group'])
        def ask_language(message):
            session = self.sessions[message.chat.id]
            markup = Markups.get_choose_language_markup(session.language)
            self.bot.send_message(chat_id=message.chat.id, text=Messages.choose_language(session.language), reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def change_session_language(call):
            session = self.sessions[call.message.chat.id]
            selected_language = call.data
            if selected_language in Messages.get_languages('english'):
                session.change_language(selected_language)
        
        @self.bot.message_handler(func=lambda message:True, chat_types=['private'])
        def repeat(message):
            self.bot.send_message(chat_id=message.chat.id, text="hello")

        @self.bot.poll_answer_handler()
        def handle_answer(poll_answer):
            self.handle_poll_answer(poll_answer)

        self.bot.polling()

