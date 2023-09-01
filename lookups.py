import telebot

def Messages(title, session):
    # what is best way to save responses?
    # it should reserve:
        # scalability: ability to accept more languages easily
        # memory: one instance for all sessions
        # clarity & specificity: messages titles should be specified here and not given as string parameters, for ease of use & readability
    # we can make it a class, but how to differentiate btw languages?
    # a function would not reserve clarity & specificity, and same for using dictionaries directly
    
    if title == 'non_spy_role_assigned':
        return f"You are not the spy. Ask questions to find the spy!\nThe word is {session.word}"
    
    def send_word(word:str):
        return f"The word is {word}"
    
    def show_results(spy: telebot.types.User, word:str):
        return f"The spy is {spy.full_name} and " + Messages.send_word(word)

class Keys:
    TOKEN = '6441490404:AAEbQ40r-hFFZAV3QQKpsvsPGON2_T40sy0'
    File_Directory = 'C:\Ali\TelegramBots\SpyGame\data.json'


