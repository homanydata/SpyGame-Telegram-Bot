import telebot
import json

class Messages():
    messages = {
        "english":{
            "start_game_prompt" : "Who wants to play the spy game? Click below to join!",
            "wonna_play" : "I am in",
            "no_enough_players" : "oops, sorry to tell you that there is no enough players to play now, try at another time",
            "spy_role_assigned" : "You are the spy!",
            "guess_spy" : "Who do you think is the spy?",
            "player_assigned": "You are not the spy. Ask questions to find the spy!\nThe word is ",
            "announce_spy": "The spy is "
            },
        "arabic":{
            "start_game_prompt" : "مين يلعب؟",
            "wonna_play" : "انا",
            "no_enough_players" : "انتو الكل بالكل بس عددكن مش كافي للعبة لازم تكونو 4 عالاقل",
            "spy_role_assigned" : "انت برا السالفة",
            "guess_spy" : "مين بتعتقد برا السالفة؟",
            "player_assigned": "الكلمة هيي ",
            "announce_spy": "اللي برا السالفة هوي "
        }
    }

    def start_game_prompt(language): return Messages.messages[language]['start_game_prompt']
    def wonna_play(language): return Messages.messages[language]['wonna_play']
    def no_enough_players(language): return Messages.messages[language]['no_enough_players']
    def spy_role_assigned(language): return Messages.messages[language]['spy_role_assigned']
    def guess_spy(language): return Messages.messages[language]['guess_spy']

    def send_word(word:str, language:str):
        return Messages.messages[language]["send_word"] + word
    
    def show_results(spy:telebot.types.User, word:str, language):
        return Messages.messages[language]["announce_spy"] + spy.full_name + "and" + Messages.send_word(word, language)

class Keys:
    TOKEN = '6441490404:AAF3m-jPebn9E4dzn9ZeoCF82CiveNzc0AU'
    File_Directory = 'C:\Ali\TelegramBots\SpyGame\data.json'

class Timer:
    waiting_players = 30
    questions_time = 180

