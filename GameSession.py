class GameSession:
    def __init__(self, chat_id) -> None:
        self.chat_id = chat_id
        self.players = []
        self.spy = None
        self.word = ''
        self.language = 'english'
