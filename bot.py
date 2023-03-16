import os
import json
import requests
import time

from copilot import Copilot
from dotenv import load_dotenv

from telegram import (
    ReplyKeyboardMarkup,
    Update,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

(ENTRY_STATE, QUESTION_STATE,
 ) = range(2)


def _generate_copilot(prompt: str):

    copilot = Copilot()
    c = copilot.get_answer(prompt)

    return c

async def start(update: Update, context: ContextTypes):

    button = [[KeyboardButton(text="Question-Answering")]]
    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True
    )

    await update.message.reply_text(
        "Choose an option: 👇🏻",
        reply_markup=reply_markup,
    )

    return ENTRY_STATE


async def pre_query_handler(update: Update, context: ContextTypes):

    button = [[KeyboardButton(text="Back")]]
    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True
    )

    await update.message.reply_text(
        "Enter your text: 👇🏻",
        reply_markup=reply_markup,
    )

    return QUESTION_STATE


async def pre_query_answer_handler(update: Update, context: ContextTypes):
    button = [[KeyboardButton(text="Back")]]
    reply_markup = ReplyKeyboardMarkup(
        button, resize_keyboard=True
    )

    question = update.message.text

    answer = _generate_copilot(question)
    context.user_data['answer'] = answer

    await update.message.reply_text(
        answer,
        reply_markup=reply_markup,
    )


if __name__ == '__main__':
    load_dotenv()

    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).read_timeout(100).get_updates_read_timeout(100).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
        ENTRY_STATE: [
        MessageHandler(filters.Regex('^Back$'), start),
        MessageHandler(filters.Regex('^Question-Answering$'), pre_query_handler),
        ],
        QUESTION_STATE: [
        MessageHandler(filters.Regex('^Back$'), start),
        MessageHandler(filters.TEXT, pre_query_answer_handler),
        ],
        },
        fallbacks=[],
    )
    
    application.add_handler(conv_handler)
    
    print("Bot is running ...")
    application.run_polling()