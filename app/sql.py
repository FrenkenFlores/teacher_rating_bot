import logging
import sqlite3 as sql
from sqlite3 import Connection, Cursor
from aiogram import Dispatcher
db: Connection


def connect_db():
    global db
    db = sql.connect("teacher_rating_bot.db")
    with db:
        # If no exceptions occur db.commit() will be executed afterwards automatically.
        try:
            db.execute(
                "CREATE TABLE IF NOT EXISTS "
                "chats("
                    "id INTEGER PRIMARY KEY , "
                    "chat_title TEXT, "
                    "chat_type TEXT, "
                    "bot_available BOOLEAN, "
                    "bot_admin BOOLEAN"
                ");"
            )
        # If an exception occurs db.rollback() will be called.
        except Exception as e:
            logging.error(e)


def add_chat_to_db(response: dict):
    """This function receives a dict object that represents data from an event."""
    with db:
        try:
            db.execute(
                "INSERT INTO "
                    "chats ("
                        "id, "
                        "chat_title, "
                        "chat_type, "
                        "bot_available, "
                        "bot_admin"
                    ") VALUES ("
                    f"{response['id']}, "
                    f"'{response['chat_title']}', "
                    f"'{response['chat_type']}', "
                    f"{'TRUE' if response['bot_available'] else 'FALSE'}, "
                    f"{'TRUE' if response['bot_admin'] else 'FALSE'}"
                ");"
            )
        except Exception as e:
            logging.error(e)


def delete_chat_from_db(id: int):
    "DELETE FROM table WHERE search_condition;"
    with db:
        try:
            db.execute(f"DELETE FROM chats WHERE id = {id};")
        except Exception as e:
            logging.error(e)


def update_chat_in_db(id: int, bot_available: bool, bot_admin: bool):
    with db:
        try:
            db.execute(
                f"UPDATE chats SET "
                    f"bot_available = {'TRUE' if bot_available else 'FALSE'}, "
                    f"bot_admin = {'TRUE' if bot_admin else 'FALSE'} "
               f"WHERE "
                    f"id = {id};"
            )
        except Exception as e:
            logging.error(e)


def get_chats_dict_from_db() -> dict:
    groups = dict()
    with db:
        try:
            list_of_rows = db.cursor().execute("SELECT * FROM chats").fetchall()
        except Exception as e:
            logging.error(e)
            list_of_rows = {}
    for row in list_of_rows:
        id, chat_title, chat_type, bot_available, bot_admin = row
        groups[id] = {
            "chat": {
                "id": id,
                "title": chat_title,
                "type": chat_type,
            },
            "bot_available": True if bot_available == "TRUE" else False,
            "bot_admin": True if bot_admin == "FALSE" else False
        }
    return groups


def close_db(dp: Dispatcher):
    logging.info("Close Database")
    db.close()
