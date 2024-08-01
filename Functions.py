from telegram import BotCommand


async def set_bot_commands(app):
    commands = [
        BotCommand('start', 'Start bot and goes to main menu'),
        BotCommand('quit', 'Quit the game and goes to main menu'),
    ]
    await app.bot.set_my_commands(commands)