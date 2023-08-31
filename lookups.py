import telebot

class Keys:
    TOKEN = '6441490404:AAEbQ40r-hFFZAV3QQKpsvsPGON2_T40sy0'
    File_Directory = 'C:\Ali\TelegramBots\SpyGame\data.json'


class Messages:
    start_game_prompt = "Who wants to play the spy game? Click below to join!"
    wonna_play = 'I am in'
    
    no_enough_players = "oops, sorry to tell you that there is no enough players to play now, try at another time"
    
    spy_role_assigned = "You are the spy!"
    def non_spy_role_assigned(word:str):
        return "You are not the spy. Ask questions to find the spy!\n" + Messages.send_word(word)
    guess_spy = "Who do you think is the spy?"
    
    correct_guess = "You guessed correctly! +1 point"
    incorrect_guess = "Incorrect guess. The spy was not caught."
    
    def send_word(word:str):
        return f"The word is {word}"
    
    def show_results(spy: telebot.types.User, word:str):
        return f"The spy is {spy.full_name} and " + Messages.send_word(word)

