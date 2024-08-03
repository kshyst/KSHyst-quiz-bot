import logging
import re

import requests
from telegram import BotCommand

import db


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


def getQuestions(cat: str) -> list:
    global data

    # Fetch data based on the category
    if cat == 'Math':
        data = db.get_all_math_questions()
    elif cat == 'Celebrities':
        data = db.get_all_celebrities_questions()
    elif cat == 'Movies':
        data = db.get_all_movies_questions()
    elif cat == 'Vehicles':
        data = db.get_all_vehicles_questions()
    elif cat == 'Anime':
        data = db.get_all_anime_questions()
    else:
        return []

    questions = []

    #TODO make it choose random
    for i, question in enumerate(data):
        if i == 5:
            break

        question_text = question['question']
        correct_answer = question['correct_answer']
        answers = question['answers'].split(',')

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
