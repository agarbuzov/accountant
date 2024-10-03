from datetime import datetime

import telebot
from sqlalchemy import func
from sqlalchemy.orm import Session
from telebot.formatting import escape_markdown

from models import engine, Operation
from settings import TELEGRAM_TOKEN, OWNER_ID

bot = telebot.TeleBot(TELEGRAM_TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("/balance", "Current balance"),
    telebot.types.BotCommand("/list", "List of specified number of recent operations, default 10"),
    telebot.types.BotCommand("/delete", "Delete operation")
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
            query = query.limit(int(args[0]))
        else:
            query = query.limit(10)

    result = session.query(query.subquery()).order_by("date").all()

    bot.reply_to(message, "\n".join([
        f"{operation.date} | {escape_markdown(operation.description)} | *{operation.value:+}*" for operation in result
    ]), parse_mode="Markdown")


@bot.message_handler(commands=["delete"])
@owner_check
def handle(message: telebot.types.Message) -> None:
    with Session(engine) as session:
        if operation := session.get(Operation, message.reply_to_message.id):
            session.delete(operation)
            session.commit()

    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message.reply_to_message.id)


@bot.message_handler(func=lambda m: True)
@owner_check
def handle(message: telebot.types.Message) -> None:
    write(message.id, *message.text.split(","))


@bot.edited_message_handler(func=lambda m: True)
@owner_check
def handle(message: telebot.types.Message) -> None:
    update(message.id, *message.text.split(","))


def write(message_id, value, description, date=None) -> None:
    with Session(engine) as session:
        operation = Operation(id=message_id, value=value.strip(), description=description.strip())
        session.add(operation)

        if date:
            operation.date = datetime.strptime(date.strip(), "%Y-%m-%d")

        session.commit()


def update(message_id, value, description, date=None) -> None:
    with Session(engine) as session:
        data = {"value": value.strip(), "description": description.strip()}

        if date:
            data["date"] = datetime.strptime(date.strip(), "%Y-%m-%d")

        session.query(Operation).filter_by(id=message_id).update(data)
        session.commit()


bot.infinity_polling()
