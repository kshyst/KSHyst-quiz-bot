import json
import Dicts
import Functions
import requests
from telegram import Update, MenuButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ApplicationBuilder, \
    ConversationHandler, filters, CallbackQueryHandler

import db

token = json.load(open('token.json'))['token']

Functions.log()

MAIN_MENU, CATEGORY, GAME = range(3)
ENTER_CORRECT_ANSWER, ENTER_ANSWER2, ENTER_ANSWER3, ENTER_ANSWER4, ENTER_QUESTION_TEXT, THANKS = range(4, 10)

markup = Dicts.markup
markup_category = Dicts.markup_category


async def start(update: Update, context: CallbackContext) -> int:
    await Functions.another_user_playing(update, context)
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text='Hello, welcome to the bot',
        reply_markup=markup,
    )

    return MAIN_MENU


async def leader_board(update: Update, context: CallbackContext) -> int:
    await Functions.another_user_playing(update, context)
    chat_id = update.effective_chat.id
    users = db.get_top_10_users()
    text = "Leader Board\n"
    for user in users:
        text += f"{user['user_name']} - {user['score']}\n"

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=markup,
    )

    return MAIN_MENU


async def info(update: Update, context: CallbackContext) -> int:
    await Functions.another_user_playing(update, context)
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text='Welcome to KSHyst quiz bot. This bot is designed to help you test your knowledge in different categories . just simply press start game and select the category and difficulty you want to play',
        reply_markup=markup,
    )

    return MAIN_MENU


async def startGame(update: Update, context: CallbackContext) -> int:
    await Functions.another_user_playing(update, context)
    chat_id = update.effective_chat.id
    context.user_data['user_id'] = update.effective_user.id
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['is_playing'] = True

    db.insert_user(user_id=update.effective_user.id, name=update.effective_user.username)

    await context.bot.send_message(
        chat_id=chat_id,
        text='Select a category',
        reply_markup=markup_category,
    )

    return CATEGORY


async def category(update: Update, context: CallbackContext) -> int:
    await Functions.you_didnt_start_game(update, context)
    chat_id = update.effective_chat.id
    context.user_data['category'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text=f'You have selected {context.user_data["category"]} category , press start to start the game',
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Start", callback_data="button")
        ),
    )

    return GAME


async def game(update: Update, context: CallbackContext) -> int:
    await Functions.you_didnt_start_game(update, context)
    chat_id = update.effective_chat.id
    question = ""
    correct_answer = ""
    answers = []

    if 'questions' not in context.user_data:
        context.user_data['questions'] = Functions.getQuestions(
            cat=context.user_data['category'],
        )
        context.user_data['score'] = 0

    #check if the answer is correct
    if update.callback_query.data in context.user_data['questions'][0]['answers']:
        correct_answer = context.user_data['questions'][0]['correct_answer']
        context.user_data['questions'].pop(0)
        if update.callback_query.data == correct_answer:
            context.user_data['score'] += 1

    #end the game
    if len(context.user_data['questions']) == 0:
        context.user_data['is_playing'] = False
        del context.user_data['questions']
        del context.chat_data['playing_users_id']
        await context.bot.send_message(
            chat_id=chat_id,
            text='Game Over your score is: ' + str(context.user_data['score']),
            reply_markup=markup,
        )
        db.update_user_score(context.user_data['user_id'], context.user_data['score'])
        return MAIN_MENU

    #send the next question
    if context.user_data['questions']:
        question = context.user_data['questions'][0]['question']
        correct_answer = context.user_data['questions'][0]['correct_answer']
        answers = context.user_data['questions'][0]['answers']
        print(answers)
        await context.bot.send_message(
            chat_id=chat_id,
            text=question,
            reply_markup=InlineKeyboardMarkup.from_column(
                [InlineKeyboardButton(text=answer, callback_data=answer) for answer in answers]
            ),
        )
        return GAME


async def enter_category(update: Update, context: CallbackContext) -> int:
    if update.effective_chat.type != 'private':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='This command only works in a private chat with this bot',
        )
        return -1
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the category',
        reply_markup=markup_category
    )

    return ENTER_QUESTION_TEXT


async def add_question(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    context.chat_data['category'] = update.message.text
    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the question text',
    )

    return ENTER_CORRECT_ANSWER


async def enter_correct_answer(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    context.chat_data['question_text'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the correct answer',
    )

    return ENTER_ANSWER2


async def enter_other_answer2(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    context.chat_data['correct_answer'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the second answer',
    )

    return ENTER_ANSWER3


async def enter_other_answer3(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    context.chat_data['answer2'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the third answer',
    )

    return ENTER_ANSWER4


async def enter_other_answer4(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    context.chat_data['answer3'] = update.message.text

    await context.bot.send_message(
        chat_id=chat_id,
        text='Enter the fourth answer',
    )

    return THANKS


async def thanks_for_adding_question(update: Update, context: CallbackContext) -> int:
    context.chat_data['answer4'] = update.message.text

    chat_id = update.effective_chat.id
    db.insert_question(
        category=context.chat_data['category'],
        question=context.chat_data['question_text'],
        correct_answer=context.chat_data['correct_answer'],
        answers=','.join([
            context.chat_data['correct_answer'],
            context.chat_data['answer2'],
            context.chat_data['answer3'],
            context.chat_data['answer4'],
        ]),
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text='Thanks for adding the question',
        reply_markup=markup,
    )

    return MAIN_MENU


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
                MessageHandler(filters.Regex("^Leader Board$"), callback=leader_board),
                ConversationHandler(
                    entry_points=[MessageHandler(filters.Regex("^Add Question$"), callback=enter_category)],
                    states={
                        ENTER_QUESTION_TEXT: [
                            MessageHandler(filters.Regex(".*"), callback=add_question),
                        ],
                        ENTER_CORRECT_ANSWER: [
                            MessageHandler(filters.Regex(".*"), callback=enter_correct_answer),
                        ],
                        ENTER_ANSWER2: [
                            MessageHandler(filters.Regex(".*"), callback=enter_other_answer2),
                        ],
                        ENTER_ANSWER3: [
                            MessageHandler(filters.Regex(".*"), callback=enter_other_answer3),
                        ],
                        ENTER_ANSWER4: [
                            MessageHandler(filters.Regex(".*"), callback=enter_other_answer4),
                        ],
                        THANKS: [
                            MessageHandler(filters.Regex(".*"), callback=thanks_for_adding_question),
                        ],
                    },
                    fallbacks=[],
                ),
            ],
            CATEGORY: [
                MessageHandler(filters.Regex("^(Celebrities|Movies|Vehicles|Anime|Math)$"), callback=category),
            ],
            GAME: [
                CallbackQueryHandler(game)
            ],
        },
        fallbacks=[CommandHandler('quit', start)],
    ))


    Functions.set_bot_commands(application)

    application.run_polling()
