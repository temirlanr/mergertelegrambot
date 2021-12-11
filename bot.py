import logging
import os
import pandas as pd

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram.files.document import Document

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8442'))

# Hide the telegram bot token
TOKEN = os.environ["TOKEN"]


START_MERGING, FIRST_FILE, SECOND_FILE = range(3)
# Functions
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Отправьте /help для справки по боту.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Вам нужно будет вызвать команду /start_merging для того чтобы бот начал принимать файлы. Бот будет просить файлы по одному так что не загружайте несколько файлов сразу, только по одному.\n\nВ любой момент можно вызвать команду /cancel чтобы отменить все.")


def start_merging(update: Update, context: CallbackContext) -> int:

    update.message.reply_text('Отправьте пожалуйста первый файл...\n\nЛибо /cancel чтобы отменить.')

    return FIRST_FILE


def first_file(update: Update, context: CallbackContext) -> int:

    global file1
    file1 = update.message.document.file_name
    update.message.document.get_file().download

    update.message.reply_text('Отправьте пожалуйста второй файл...\n\nЛибо /cancel чтобы отменить.')

    return SECOND_FILE


def second_file(update: Update, context: CallbackContext) -> int:

    global file2
    file2 = update.message.document.file_name
    update.message.document.get_file().download

    first = pd.read_excel(file1)
    second = pd.read_excel(file2)

    first.rename(columns={"Контрагент": "Плательщик"}, inplace=True)
    second.rename(columns={"Контрагент": "Плательщик"}, inplace=True)

    merged = pd.merge(first, second, on=['Сумма', 'Плательщик'], how='outer')
    merged.to_excel('result.xlsx', index=False)

    context.bot.send_document(chat_id=update.effective_chat.id, document='result.xlsx')

    update.message.reply_text('Готово!')

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
                                       states={FIRST_FILE: [CommandHandler('cancel', cancel), MessageHandler(Filters.document, first_file)],
                                               SECOND_FILE: [CommandHandler('cancel', cancel), MessageHandler(Filters.document, second_file)],},
                                       fallbacks=[CommandHandler('cancel', cancel)],))

    # on noncommand i.e message - echo the message on Telegram

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN, 
                          webhook_url="https://mergertelegrambot.herokuapp.com//" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()