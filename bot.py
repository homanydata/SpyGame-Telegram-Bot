import telebot
from telebot.types import PollAnswer, Chat
from lookups import Keys, Messages, Timer, Errors, Markups
from json_handler import read_dict
import threading
from GameSession import GameSession

class SpyGameBot:
    def __init__(self):
        self.bot = telebot.TeleBot(Keys.TOKEN)
        self.dic = read_dict()
        self.sessions = {}
        self.private_chats_language = {}
        self.poll_chat_ids = {}

    def start(self, chat_id):
        # if it is old group, restart turn-related attributes
        if self.is_session(chat_id=chat_id):
            self.sessions[chat_id].restart_session()
        # if it's new group, create a session for it & add it to sessions dictionary attribute
        else:
            self.create_session(chat_id=chat_id)        
        
        session = self.sessions[chat_id]
        
        # send participation poll
        sent_message = self.bot.send_poll(chat_id=chat_id, question=Messages.start_game_prompt(session.language), options=[Messages.wonna_play(language=session.language)]*2, is_anonymous=False, open_period=Timer.waiting_players)
        poll = sent_message.poll
        
        # map this poll_id to its chat_id to be able to know for which chat is a pollAnswer object
        self.poll_chat_ids[poll.id] = chat_id
        
        # wait till users join the game and vote, then check if they are enough to start a turn
        self.start_timer(time=Timer.waiting_players, function=self.check_enough_players, kwargs={"session":session})

    def check_enough_players(self, session):
        # are players enough?
        if len(session.players) >= Keys.min_players:
            # prepare for the turn
            session.choose_spy()
            session.choose_word(dic=self.dic)
            
            # send private msg for each player
            # this method returns False if it's not able to reach some players, so turn is stopped, group is told that within the function
            if not self.send_private_messages(session=session):
                return
            # tell the players to start asking each other
            self.bot.send_message(chat_id=session.chat_id, text=Messages.start_questions(language=session.language))
            # start timer for questions in the group chat
            self.start_timer(time=Timer.questions_time, function=self.guessing_time, kwargs={"session":session})
        else:
            # if players are not enough send that
            self.bot.send_message(chat_id=session.chat_id, text=Messages.no_enough_players(language=session.language))

    def show_results(self, session):
        # when a turn ends, announce who is the spy and what is the word
        self.bot.send_message(chat_id=session.chat_id, text=Messages.show_results(spy=session.spy, word=session.word,language=session.language))

    def start_timer(self, function, time, kwargs):
        timer = threading.Timer(interval=time, function=function, kwargs=kwargs)
        timer.start()

    def send_private_messages(self, session:GameSession):
        all_good = True
        for player in session.players:
            # for each player send a message according to its type
            try:
                if player != session.spy:
                    # if player send the word
                    self.bot.send_message(chat_id=player.id, text=Messages.send_word(word=session.word,language=session.language))
                else:
                    # if spy tell him he is a spy
                    self.bot.send_message(chat_id=player.id, text=Messages.spy_role_assigned(language=session.language))
            except Exception as e:
                # if a player is a new user, the bot cannot chat him, send that to group and return False to stop the turn
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
        # if it is guessing spy poll, pass, till now
        else:
            pass

    def guessing_time(self, session:GameSession):
        # send poll to group chat for players to try to guess who is the spy
        self.bot.send_poll(chat_id=session.chat_id, question=Messages.guess_spy(language=session.language), options=session.players_options(), open_period=Timer.guessing_spy)
        
        # start timer for poll time until results shown
        self.start_timer(time=Timer.guessing_spy, function=self.show_results, kwargs={"session":session})

    def get_chat_language(self, chat_id):
        # if this chat is private and known, we send the intro in its preferrable language
        if chat_id in self.private_chats_language.keys():
            language = self.private_chats_language[chat_id]
        # if chat is a session
        elif chat_id in self.sessions.keys():
            language = self.sessions[chat_id].language
        # else send it in default language
        else:
            language = Keys.Default_Language
        
        return language
    
    def is_private_chat(self, chat_id):
        return chat_id in self.private_chats_language.keys()
    
    def is_session(self,chat_id):
        result = chat_id in self.sessions.keys()
        return result
    
    def create_session(self, chat_id):
        new_session = GameSession(chat_id=chat_id)
        self.sessions[chat_id] = new_session

    def run(self):
        # the bot introduces itself
        @self.bot.message_handler(commands=['help'])
        def introduce_bot(message):
            # send bot description on this chat using its preferrable language
            language = self.get_chat_language(chat_id=message.chat.id)
            self.bot.send_message(chat_id=message.chat.id, text=Messages.help(language))
        
        @self.bot.message_handler(commands=['change_language'])
        def ask_language(message):
            # ask for the language the user wants using a markup
            language = self.get_chat_language(message.chat.id)
            markup = Markups.get_choose_language_markup(language)
            self.bot.send_message(chat_id=message.chat.id, text=Messages.choose_language(language), reply_markup=markup)
        
        @self.bot.callback_query_handler(func= lambda call:True)
        def change_language(call):
            # the only callback this bot may recieve is on language changing markup, which will hold selected language 
            selected_language = call.data
            chat_id = call.message.chat.id

            if call.message.chat.type == 'private':
                # if this is not a session, save the language of this private chat in the private chats-language dictionary attribute
                self.private_chats_language[chat_id] = selected_language
            else: #it is a group chat
                if chat_id not in self.sessions:
                    # if new group create new session & add it to sessions attribute
                    self.create_session(chat_id=chat_id)
                # change language of this session
                self.sessions[chat_id].change_language(selected_language)
            
            # whatever the chat is, send DONE message in new selected language
            self.bot.send_message(chat_id=chat_id, text=Messages.language_changed(selected_language))

        # the bot is not made for private chats, so for any message in a private chat other than /help, it will just respond with "hello"
        @self.bot.message_handler(chat_types=['private'])
        def hello(message):
            self.bot.send_message(chat_id=message.chat.id, text="hello")

        @self.bot.message_handler(commands=['play'])
        def handle_play_command(message):
            # here the game starts
            self.start(chat_id=message.chat.id)
        
        @self.bot.poll_answer_handler()
        def handle_answer(poll_answer):
            # a poll answer is either for participation or guessing the spy polls
            self.handle_poll_answer(poll_answer)
        
        @self.bot.message_handler(content_types=['new_chat_members'])
        def new_chat_member(message):
            chat_id = message.chat.id
            new_members = message.new_chat_members

            for member in new_members:
                if member.id == self.bot.get_me().id:
                    # The bot itself was added to the group
                    introduce_bot(message)
                else:
                    # Other members were added to the group
                    language = self.get_chat_language(chat_id=chat_id)
                    self.bot.send_message(chat_id, Messages.welcome(member, language=language))
        self.bot.polling()

