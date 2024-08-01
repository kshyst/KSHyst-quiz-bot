import json
import logging

import telegram

import Functions
import requests
from telegram import Update, MenuButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ApplicationBuilder, \
    ConversationHandler, filters, CallbackQueryHandler

token = json.load(open('token.json'))['token']

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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

MAIN_MENU, CATEGORY, DIFFICULTY, GAME = range(4)

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


def getQuestions(cat: str, diff: str) -> list:
    category_id = category_id_dict[cat]
    difficult = difficulty_dict[diff]
    api_url = f"https://opentdb.com/api.php?amount=5&category={category_id}&difficulty={difficult}&type=multiple"

    response = requests.get(api_url)
    data = response.json()['results']

    questions = []

    for question in data:
        question_text = question['question']
        correct_answer = question['correct_answer']
        incorrect_answers = question['incorrect_answers']

        answers = incorrect_answers + [correct_answer]
        answers.sort()

        questions.append({
            'question': question_text,
            'correct_answer': correct_answer,
            'answers': answers,
        })

    return questions


async def start(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    if 'playing_users_id' not in context.chat_data:
        context.chat_data['playing_users_id'] = update.effective_user.id
    elif context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Another user is already playing the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1

    if update.effective_chat.type == 'private':
        await context.bot.send_message(
            chat_id=chat_id,
            text='Please Start the bot in a group chat',
        )
        return -1

    await context.bot.send_message(
        chat_id=chat_id,
        text='Hello, welcome to the bot',
        reply_markup=markup,
    )

    return MAIN_MENU


async def info(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    if context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are not the one who started the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1

    await context.bot.send_message(
        chat_id=chat_id,
        text='Welcome to KSHyst quiz bot. This bot is designed to help you test your knowledge in different categories . just simply press start game and select the category and difficulty you want to play',
        reply_markup=markup,
    )

    return MAIN_MENU


async def startGame(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    if 'playing_users_id' not in context.chat_data:
        context.chat_data['playing_users_id'] = update.effective_user.id
    elif context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Another user is already playing the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1
    context.user_data['user_id'] = update.effective_user.id
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['is_playing'] = True

    await context.bot.send_message(
        chat_id=chat_id,
        text='Select a category',
        reply_markup=markup_category,
    )

    return CATEGORY


async def category(update: Update, context: CallbackContext) -> int:
    if context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are not the one who started the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1

    chat_id = update.effective_chat.id
    context.user_data['category'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text='Select a difficulty',
        reply_markup=markup_difficulty,
    )

    return DIFFICULTY


async def difficulty(update: Update, context: CallbackContext) -> int:
    if context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are not the one who started the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1
    chat_id = update.effective_chat.id
    context.user_data['difficulty'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text=f'You have selected {context.user_data["category"]} category and {context.user_data["difficulty"]} difficulty',
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Start", callback_data="button")
        ),
    )

    return GAME


async def game(update: Update, context: CallbackContext) -> int:
    if context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are not the one who started the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1

    chat_id = update.effective_chat.id
    question = ""
    correct_answer = ""
    answers = []

    if 'questions' not in context.user_data:
        context.user_data['questions'] = getQuestions(
            cat=context.user_data['category'],
            diff=context.user_data['difficulty'],
        )
        context.user_data['score'] = 0

    if update.callback_query.data in context.user_data['questions'][0]['answers']:
        correct_answer = context.user_data['questions'][0]['correct_answer']
        context.user_data['questions'].pop(0)
        if update.callback_query.data == correct_answer:
            context.user_data['score'] += 1 * difficulty_multiplier[context.user_data['difficulty']]

    if len(context.user_data['questions']) == 0:
        context.user_data['is_playing'] = False
        del context.user_data['questions']
        del context.chat_data['playing_users_id']
        await context.bot.send_message(
            chat_id=chat_id,
            text='Game Over your score is: ' + str(context.user_data['score']),
            reply_markup=markup,
        )
        return MAIN_MENU

    if context.user_data['questions']:
        question = context.user_data['questions'][0]['question']
        correct_answer = context.user_data['questions'][0]['correct_answer']
        answers = context.user_data['questions'][0]['answers']

        await context.bot.send_message(
            chat_id=chat_id,
            text=question,
            reply_markup=InlineKeyboardMarkup.from_column(
                [InlineKeyboardButton(text=answer, callback_data=answer) for answer in answers]
            ),
        )
        return GAME


if __name__ == '__main__':

    application = ApplicationBuilder().token(token).build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(filters.Regex("^Start Game$"), callback=startGame),
                      MessageHandler(filters.Regex("^Start$"), callback=start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex("^Start Game$"), callback=startGame),
                MessageHandler(filters.Regex("^Info$"), callback=info),
                MessageHandler(filters.Regex("^Leader Board$"), callback=start),
            ],
            CATEGORY: [
                MessageHandler(filters.Regex("^(Celebrities|Movies|Vehicles|Anime|Math)$"), callback=category),
            ],
            DIFFICULTY: [
                MessageHandler(filters.Regex("^(Easy|Medium|Hard)$"), callback=difficulty),
            ],
            GAME: [
                CallbackQueryHandler(game)
            ],
        },
        fallbacks=[CommandHandler('quit', start)],
    ))

    #Functions.set_bot_commands(application)

    application.run_polling()
