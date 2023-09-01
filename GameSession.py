class GameSession:
    def __init__(self, chat_id) -> None:
        self.group_chat_id = chat_id
        self.restart_session()
        self.players = []
        self.spy = None
        self.word = ''
        language = ''
