# SpyGame
A Telegram Bot that helps any group he is in to play Spy Game online together

## Components
- Game Session:
A game session is a group of players that play Spy Game together. Each game session has:
    - Chat ID
    - Language (arabic/english)
    - Players
    - Word
    - Spy
- Bot:
Represents the game manager, has different attributes to help keep the game running and manager several games simultaneaosly:
    - Telegram Bot Instance
    - Game Sessions objects
    - Private chat languages to remember which language each chat used
    - Poll Chat IDs: dictionaty to relate each poll to a group
- Lookups:
Offers all constants needed and helping methods
- JSON Handler:
Reads json file and helps choose random words


## Bot Commands
- help: what is this bot?
- change_language: choose between Arabic & English for the chat & Game
- play: start a new turn in this group

## Usage
You can find the bot [here](https://t.me/arabic_spy_game_bot)
- Bot is invoked using /play in a telegram group
- It asks who wants to play using a poll
- Sends a private message for each of the participants, either the keyword or "you are a spy"
- Starts a timer for the players to ask each other questions
- At the end it sends a poll for guessing the spy
- Finally, it shows the results, and records points for safe spies and correct guesses.

Simple and clear just add it to your group and have fun :)

You can try the bot here : https://t.me/arabic_spy_game_bot