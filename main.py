import json
import Dicts
import Functions
import requests
from telegram import Update, MenuButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ApplicationBuilder, \
    ConversationHandler, filters, CallbackQueryHandler

token = json.load(open('token.json'))['token']

Functions.log()

MAIN_MENU, CATEGORY, DIFFICULTY, GAME = range(4)

markup = Dicts.markup
markup_category = Dicts.markup_category
markup_difficulty = Dicts.markup_difficulty
category_id_dict = Dicts.category_id_dict
difficulty_dict = Dicts.difficulty_dict
difficulty_multiplier = Dicts.difficulty_multiplier

async def start(update: Update, context: CallbackContext) -> int:
    await Functions.another_user_playing(update, context)
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text='Hello, welcome to the bot',
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
        text='Select a difficulty',
        reply_markup=markup_difficulty,
    )

    return DIFFICULTY


async def difficulty(update: Update, context: CallbackContext) -> int:
    await Functions.you_didnt_start_game(update, context)
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
    await Functions.you_didnt_start_game(update, context)
    chat_id = update.effective_chat.id
    question = ""
    correct_answer = ""
    answers = []

    if 'questions' not in context.user_data:
        context.user_data['questions'] = Functions.getQuestions(
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

    Functions.set_bot_commands(application)

    application.run_polling()
