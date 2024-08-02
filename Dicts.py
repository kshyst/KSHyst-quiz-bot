from telegram import ReplyKeyboardMarkup


categories = ['Math', 'Celebrities', 'Movies', 'Vehicles', 'Anime']

reply_keyboard = [
    ["Start Game", "Leader Board"],
    # ["Number of siblings", "Something else..."],
    ["Info"], ["Add Question"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_category = [
    # ["Celebrities", "Movies"],
    # ["Vehicles", "Anime"],
    ["Math"],
]

markup_category = ReplyKeyboardMarkup(reply_keyboard_category, one_time_keyboard=True)

