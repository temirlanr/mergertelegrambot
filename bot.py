import logging
import os
import pandas as pd

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8442'))

# Hide the telegram bot token
TOKEN = os.environ["TOKEN"]


START_MERGING, FIRST_FILE, SECOND_FILE, RESULT = range(4)
# Functions
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Я тут чтобы помочь. Отправь /help для справки по боту.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text()


def start_merging(update: Update, context: CallbackContext) -> int:

    return FIRST_FILE


def first_file(update: Update, context: CallbackContext) -> int:

    return SECOND_FILE


def second_file(update: Update, context: CallbackContext) -> int:

    return RESULT


def result(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(
        'Передумали значит...', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(ConversationHandler(entry_points=[CommandHandler('start_merging', start_merging)],
                                       states={FIRST_FILE: [CommandHandler('cancel', cancel), MessageHandler(first_file)],
                                               SECOND_FILE: [CommandHandler('cancel', cancel), MessageHandler(second_file)],
                                               RESULT: [CommandHandler('cancel', cancel), MessageHandler(result)],},
                                       fallbacks=[CommandHandler('cancel', cancel)],))

    # on noncommand i.e message - echo the message on Telegram

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN, 
                          webhook_url="https://somesecretsantabot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()