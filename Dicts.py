from telegram import ReplyKeyboardMarkup

category_id_dict = {
    'Celebrities': 26,
    'Movies': 11,
    'Vehicles': 28,
    'Anime': 31,
    'Math': 19,
}

difficulty_dict = {
    'Easy': 'easy',
    'Medium': 'medium',
    'Hard': 'hard',
}

difficulty_multiplier = {
    'Easy': 1,
    'Medium': 2,
    'Hard': 3,
}

reply_keyboard = [
    ["Start Game", "Leader Board"],
    # ["Number of siblings", "Something else..."],
    ["Info"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_category = [
    ["Celebrities", "Movies"],
    ["Vehicles", "Anime"],
    ["Math"],
]

markup_category = ReplyKeyboardMarkup(reply_keyboard_category, one_time_keyboard=True)

reply_keyboard_difficulty = [
    ["Easy", "Medium", "Hard"],
]

markup_difficulty = ReplyKeyboardMarkup(reply_keyboard_difficulty, one_time_keyboard=True)