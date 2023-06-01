import sqlite3 as sql

db: sql.Connection
cursor: sql.Cursor

def connect_db():
    global db, cursor
    db = sql.connect("teacher_rating_bot.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS "
                    "chats("
                        "id INTEGER PRIMARY KEY , "
                        "chat_title TEXT, "
                        "chat_type TEXT, "
                        "bot_available BOOLEAN, "
                        "bot_admin BOOLEAN"
                   ");"
    )
    db.commit()


def add_chat_to_db(response: dict):
    """This function receives a dict object that represents data from an event."""
    cursor.execute("INSERT INTO "
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
    db.commit()


def delete_chat_from_db(id: int):
    "DELETE FROM table WHERE search_condition;"
    cursor.execute(f"DELETE FROM chats WHERE id = {id};")
    db.commit()


def update_chat_in_db(id: int, bot_available: bool, bot_admin: bool):
    cursor.execute(f"UPDATE chats SET "
                        f"bot_available = {'TRUE' if bot_available else 'FALSE'}, "
                        f"bot_admin = {'TRUE' if bot_admin else 'FALSE'} "
                   f"WHERE "
                        f"id = {id};")
    db.commit()


def get_chats_dict_from_db() -> dict:
    groups = dict()
    cursor.execute("SELECT * FROM chats")
    list_of_rows = cursor.fetchall()
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
