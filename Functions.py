import logging

import requests
from telegram import BotCommand

from Dicts import category_id_dict, difficulty_dict


async def set_bot_commands(application):
    commands = [
        BotCommand('start', 'Start bot and goes to main menu'),
        BotCommand('quit', 'Quit the game and goes to main menu'),
    ]
    await application.bot.set_my_commands(commands)


async def you_didnt_start_game(update, context):
    if context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are not the one who started the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1


async def another_user_playing(update, context):
    if 'playing_users_id' not in context.chat_data:
        context.chat_data['playing_users_id'] = update.effective_user.id
    elif context.chat_data['playing_users_id'] != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Another user is already playing the game',
            reply_to_message_id=update.message.message_id,
        )
        return -1


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


def log():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
