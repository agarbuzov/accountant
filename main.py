from datetime import datetime

import telebot
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import engine, Operation
from settings import TELEGRAM_TOKEN, OWNER_ID

bot = telebot.TeleBot(TELEGRAM_TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("/balance", "Current balance"),
    telebot.types.BotCommand("/list", "List of specified number of recent operations, default 10")
])


def owner_check(func):
    def wrapper(*args, **kwargs):
        if args[0].from_user.id == OWNER_ID:
            func(*args, **kwargs)
    return wrapper


@bot.message_handler(commands=["balance"])
@owner_check
def handle(message: telebot.types.Message) -> None:
    with Session(engine) as session:
        value = session.query(func.sum(Operation.value)).scalar()
    bot.reply_to(message, value)


@bot.message_handler(commands=["list"])
@owner_check
def handle(message: telebot.types.Message) -> None:
    with Session(engine) as session:
        query = session.query(Operation).order_by(Operation.date.desc())

        if args := message.text.split()[1:]:
            query.limit(int(args[0]))

    bot.reply_to(message, "\n".join([
        f"{operation.date} {operation.description} *{operation.value:+}*" for operation in query.all()
    ]), parse_mode="Markdown")


@bot.message_handler(func=lambda m: True)
@owner_check
def handle(message: telebot.types.Message) -> None:
    write(*message.text.split())


def write(value, description, date=None) -> None:
    with Session(engine) as session:
        operation = Operation(value=value, description=description)
        session.add(operation)

        if date:
            operation.date = datetime.strptime(date, "%Y-%m-%d")

        session.commit()


bot.infinity_polling()
