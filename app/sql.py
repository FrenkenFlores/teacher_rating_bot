import logging
import sqlite3 as sql
from sqlite3 import Connection, Cursor
from aiogram import Dispatcher
import json


QUESTIONS_PATH = "questions.json"
DB_PATH = "teacher_rating_bot.db"

def connect_db():
    with sql.connect(DB_PATH) as db:
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
        try:
            # Open the json file that contains questions.
            with open(QUESTIONS_PATH, "r") as json_questions:
                questions: dict = json.load(json_questions)
            if questions:
                param_list: str = " TEXT, ".join([key for key in questions]) + " TEXT"
                db.execute(
                    "CREATE TABLE IF NOT EXISTS "
                    "teachers("
                        "id TEXT PRIMARY KEY , "
                        + param_list +
                    ");"
                )
        # If an exception occurs db.rollback() will be called.
        except Exception as e:
            logging.error(e)


def add_chat_to_db(response: dict):
    """This function receives a dict object that represents data from an event."""
    with sql.connect(DB_PATH) as db:
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


def add_teacher_to_db(name: str):
    """This function receives a dict object that represents data from an event."""
    with sql.connect(DB_PATH) as db:
        try:
            # Open the json file that contains questions.
            with open(QUESTIONS_PATH, "r") as json_questions:
                questions: dict = json.load(json_questions)
            if questions:
                param_list: str = ", ".join([key for key in questions])
                init_list: str = "'" + "', '".join(["0" for key in questions]) + "'"
                db.execute(
                    "INSERT INTO "
                        "teachers ("
                            "id, "
                            + param_list +
                        ") VALUES ("
                        f"'{name}', "
                        + init_list +
                    ");"
                )
        except Exception as e:
            logging.error(e)


def delete_chat_from_db(chat_id: int):
    "DELETE FROM table WHERE search_condition;"
    with sql.connect(DB_PATH) as db:
        try:
            db.execute(f"DELETE FROM chats WHERE id = {chat_id};")
        except Exception as e:
            logging.error(e)


def delete_teacher_from_db(teacher_id: str):
    "DELETE FROM table WHERE search_condition;"
    with sql.connect(DB_PATH) as db:
        try:
            db.execute(f"DELETE FROM teachers WHERE id = '{teacher_id}';")
        except Exception as e:
            logging.error(e)


def update_chat_in_db(chat_id: int, bot_available: bool, bot_admin: bool):
    with sql.connect(DB_PATH) as db:
        try:
            db.execute(
                f"UPDATE chats SET "
                    f"bot_available = {'TRUE' if bot_available else 'FALSE'}, "
                    f"bot_admin = {'TRUE' if bot_admin else 'FALSE'} "
               f"WHERE "
                    f"id = {chat_id};"
            )
        except Exception as e:
            logging.error(e)


def update_teachers_in_db(teacher_id: str, scores: list):
    questions_dict = dict()
    with open(QUESTIONS_PATH, "r") as questions_json_file:
        questions_dict: dict = json.load(questions_json_file)
        questions_list: list = [q for q in questions_dict.keys()]
    if not questions_dict:
        logging.error("Failed to read questions")
        return
    with sql.connect(DB_PATH) as db:
        try:
            print(
                f"UPDATE teachers SET "
                    + ", ".join([f'{q} = {a}' for q, a in zip(questions_list, scores)]) + " "
               f"WHERE "
                    f"id = {teacher_id};")
            db.execute(
                f"UPDATE teachers SET "
                    + ", ".join([f'{q} = {a}' for q, a in zip(questions_list, scores)]) + " "
               f"WHERE "
                    f"id = '{teacher_id}';"
            )
        except Exception as e:
            logging.error(e)


def get_chats_dict_from_db() -> dict:
    groups = dict()
    with sql.connect(DB_PATH) as db:
        try:
            list_of_rows = db.cursor().execute("SELECT * FROM chats").fetchall()
        except Exception as e:
            logging.error(e)
            list_of_rows = {}
    for row in list_of_rows:
        chat_id, chat_title, chat_type, bot_available, bot_admin = row
        groups[chat_id] = {
            "chat": {
                "id": chat_id,
                "title": chat_title,
                "type": chat_type,
            },
            "bot_available": True if bot_available == "TRUE" else False,
            "bot_admin": True if bot_admin == "FALSE" else False
        }
    return groups


def get_teachers_dict_from_db() -> dict:
    teachers = dict()
    questions_dict = dict()
    with open(QUESTIONS_PATH, "r") as questions_json_file:
        questions_dict: dict = json.load(questions_json_file)
        questions_list: list = [q for q in questions_dict.values()]
    if not questions_dict:
        logging.error("Failed to read questions")
        return {}
    with sql.connect(DB_PATH) as db:
        try:
            list_of_rows = db.cursor().execute("SELECT * FROM teachers").fetchall()
        except Exception as e:
            logging.error(e)
            list_of_rows = {}
    for row in list_of_rows:
        teacher_id: str = row[0]
        answers = row[1:]
        for q, a in zip(questions_list, answers):
            if teacher_id not in teachers:
                teachers[teacher_id] = {
                    q: a
                }
            else:
                teachers[teacher_id].update({q: a})
    return teachers
