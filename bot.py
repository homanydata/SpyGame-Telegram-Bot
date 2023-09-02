import telebot
from telebot.types import PollAnswer
from lookups import Keys, Messages, Timer, Errors, Markups
from json_handler import read_dict
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
            session = self.sessions[chat_id]
            session.restart_session()
            self.sessions[chat_id] = session
        except:
            session = GameSession(chat_id)
            self.sessions[chat_id] = session
        
        # send poll
        sent_message = self.bot.send_poll(chat_id=session.chat_id, question=Messages.start_game_prompt(session.language), options=[Messages.wonna_play(language=session.language)]*2, is_anonymous=False, open_period=Timer.waiting_players)
        poll = sent_message.poll
        
        # map this poll_id to its chat_id
        self.poll_chat_ids[poll.id] = chat_id
        
        # wait till users join the game and vote
        self.start_timer(time=Timer.waiting_players, function=self.check_enough_players, kwargs={"session":session})

    def check_enough_players(self, session):
        if len(session.players) >= Keys.min_players:
            session.choose_spy()
            session.choose_word(dic=self.dic)
            
            # send private msg for each player
            if not self.send_private_messages(session=session):
                return
            self.bot.send_message(chat_id=session.chat_id, text=Messages.start_questions(language=session.language))
            # start timer for questions in the group chat
            self.start_timer(time=Timer.questions_time, function=self.guessing_time, kwargs={"session":session})
        else:
            self.bot.send_message(chat_id=session.chat_id, text=Messages.no_enough_players(language=session.language))

    def show_results(self, session):
        self.bot.send_message(chat_id=session.chat_id, text=Messages.show_results(spy=session.spy, word=session.word,language=session.language))

    def start_timer(self, function, time, kwargs):
        timer = threading.Timer(interval=time, function=function, kwargs=kwargs)
        timer.start()

    def send_private_messages(self, session:GameSession):
        all_good = True
        for player in session.players:
            try:
                if player != session.spy:
                    self.bot.send_message(chat_id=player.id, text=Messages.send_word(word=session.word,language=session.language))
                else:
                    self.bot.send_message(chat_id=player.id, text=Messages.spy_role_assigned(language=session.language))
            except Exception as e:
                self.bot.send_message(chat_id=session.chat_id, text=Errors.newUserError(language=session.language, user=player))
                all_good = False
        return all_good
    
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
        self.bot.send_poll(chat_id=session.chat_id, question=Messages.guess_spy(language=session.language), options=options, open_period=Timer.guessing_spy)
        # start timer for poll time until results shown
        self.start_timer(time=Timer.guessing_spy, function=self.show_results, kwargs={"session":session})

    def run(self):
        @self.bot.message_handler(chat_types=['private'])
        def repeat(message):
            self.bot.send_message(chat_id=message.chat.id, text="hello")

        @self.bot.message_handler(commands=['play'])
        def handle_play_command(message):
            self.start(chat_id=message.chat.id)
        
        @self.bot.message_handler(commands=['change_language'])
        def ask_language(message):
            try:
                session = self.sessions[message.chat.id]
            except:
                self.sessions[message.chat.id] = GameSession(chat_id=message.chat.id)
                session = self.sessions[message.chat.id]
            finally:
                markup = Markups.get_choose_language_markup(session.language)
                self.bot.send_message(chat_id=message.chat.id, text=Messages.choose_language(session.language), reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def change_session_language(call):
            session = self.sessions[call.message.chat.id]
            selected_language = call.data
            if selected_language in Messages.get_languages('english'):
                session.change_language(selected_language)
                self.bot.send_message(chat_id=session.chat_id, text=Messages.language_changed(session.language))

        @self.bot.poll_answer_handler()
        def handle_answer(poll_answer):
            self.handle_poll_answer(poll_answer)

        self.bot.polling()

