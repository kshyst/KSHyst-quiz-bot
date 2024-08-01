
class Player:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.category = None
        self.difficulty = None
        self.score = 0

    def __str__(self):
        return f"Player {self.user_id} with category {self.category} and difficulty {self.difficulty} has a score of {self.score}"
