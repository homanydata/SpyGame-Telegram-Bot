import telebot

class Keys:
    TOKEN = '6441490404:AAEcSqJo_Z3ucMJh-g7gZpJXoL7XzOwi82g'
    File_Directory = 'C:\Ali\TelegramBots\SpyGame\data.json'
    min_players = 3

class Timer:
    waiting_players = 30
    questions_time = 180
    guessing_spy = 20

class Messages():

    messages = {
        "english":{
            "start_game_prompt" : "Who wants to play the spy game? Click below to join!",
            "wonna_play" : "I am in",
            "no_enough_players" : f"oops, sorry to tell you that there is no enough players({Keys.min_players}+) to play now, try at another time",
            "spy_role_assigned" : "You are the spy!",
            "guess_spy" : "Who do you think is the spy?",
            "player_assigned": "You are not the spy. Ask questions to find the spy!\nThe word is ",
            "announce_spy": "The spy is ",
            "send_word": "The word is ",
            "choose_language": "which language do you want?",
            "get_languages": ["english","arabic"],
            "start_questions": f"Game Started!!\nask each other questions and chat to try to know who is the spy\nyou have {Timer.questions_time//60} minutes and {Timer.questions_time%60} seconds",
            "and": " and ",
            "language_changed": "Language changed successfully"
            },
        "arabic":{
            "start_game_prompt" : "مين بدو يلعب؟",
            "wonna_play" : "انا",
            "no_enough_players" : f"انتو الكل بالكل بس عددكن مش كافي للعبة لازم تكونو {Keys.min_players} عالاقل",
            "spy_role_assigned" : "انت برا السالفة",
            "guess_spy" : "مين بتعتقد برا السالفة؟",
            "player_assigned": "الكلمة هيي ",
            "announce_spy": "اللي برا السالفة هوي ",
            "send_word": "الكلمة هيي: ",
            "choose_language": "ايا لغة بدكن؟",
            "get_languages": ["انجليزي","عربي"],
            "start_questions": f"بلشنااا\nاسألو بعض اسئلة وتحدثو لتحاولو تكشفو مين برا السالفة، معكن {Timer.questions_time//60} دقايق و {Timer.questions_time%60} ثواني",
            "and": " و ",
            "language_changed": "غيرنالكن اللغة تكرم عينكن"
        }
    }

    def start_game_prompt(language): return Messages.messages[language]['start_game_prompt']
    def wonna_play(language): return Messages.messages[language]['wonna_play']
    def no_enough_players(language): return Messages.messages[language]['no_enough_players']
    def start_questions(language): return Messages.messages[language]['start_questions']
    def spy_role_assigned(language): return Messages.messages[language]['spy_role_assigned']
    def guess_spy(language): return Messages.messages[language]['guess_spy']
    def choose_language(language): return Messages.messages[language]['choose_language']
    def language_changed(language): return Messages.messages[language]['language_changed']
    def get_languages(language): return Messages.messages[language]['get_languages']
    def and_word(language): return Messages.messages[language]['and']

    def send_word(word:str, language:str):
        return Messages.messages[language]["send_word"] + word
    
    def show_results(spy:telebot.types.User, word:str, language):
        return f'{Messages.messages[language]["announce_spy"]} @{spy.username} {Messages.and_word(language)} {Messages.send_word(word, language)}'

class Errors:
    errors = {
        "english":{
            'newUserError': ", sorry to say I have never chatted with you before so can you start a private chat?\nI cannot start a turn if I don't know all players"
        },
        "arabic":{
            'newUserError': '، ما بقدر احكي حدا اذا ولا مرة باعتلي شي، بعتلي حيلا شي عالخاص'
        }
    }
    def newUserError(language:str, user:telebot.types.User): return f"@{user.username} {Errors.errors[language]['newUserError']}"

class Markups:
    def get_choose_language_markup(language):
        markup = telebot.types.InlineKeyboardMarkup(row_width=len(Messages.get_languages('english'))//2)
        buttons = [
            telebot.types.InlineKeyboardButton(language, callback_data=standard) for language, standard in zip(Messages.get_languages(language), Messages.get_languages('english'))
        ]
        markup.add(*buttons)
        return markup
