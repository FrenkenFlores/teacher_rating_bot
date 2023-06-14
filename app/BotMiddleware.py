import logging
import json
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update
import copy
import sql


class BotMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # Connect to DataBase.
        sql.connect_db()
        # Create a dict that will be synchronized with the DataBase.
        # This dict will hold the groups where the bot was added.
        # The key will be the id of the group, the value will hold
        # boolean values that indicates whether the bot is added or removed
        # or whether the bot is an admin or not.
        self.groups: dict = sql.get_chats_dict_from_db()

    async def on_process_update(self, update: Update, data: dict):
        self.groups: dict = sql.get_chats_dict_from_db()
        update = dict(update)
        if update.get("my_chat_member"):
            # The bot was added to the supergroup.
            if update["my_chat_member"]["old_chat_member"]["status"] == "left" and \
                    update["my_chat_member"]["new_chat_member"]["status"] == "member":
                if update["my_chat_member"]["chat"]["id"] in self.groups:
                    return
                self.groups[update["my_chat_member"]["chat"]["id"]] = {
                    "chat": copy.deepcopy(update["my_chat_member"]["chat"]),
                    "bot_available": True,
                    "bot_admin": False
                }
                sql.add_chat_to_db(
                    {
                        "id": update["my_chat_member"]["chat"]["id"],
                        "chat_title": update["my_chat_member"]["chat"]["title"],
                        "chat_type": update["my_chat_member"]["chat"]["type"],
                        "bot_available": True,
                        "bot_admin": False
                    }
                )
                logging.info("add_chat_to_db", self.groups[update["my_chat_member"]["chat"]["id"]])
            # the bot was removed from the supergroup.
            elif update["my_chat_member"]["old_chat_member"]["status"] == "member" and \
                    update["my_chat_member"]["new_chat_member"]["status"] == "left":
                if self.groups.get(update["my_chat_member"]["chat"]["id"]):
                    self.groups[update["my_chat_member"]["chat"]["id"]].update(
                        {"bot_available": False}
                    )
                    sql.delete_chat_from_db(chat_id=update["my_chat_member"]["chat"]["id"])
                    logging.info("delete_chat_from_db", self.groups[update["my_chat_member"]["chat"]["id"]])
            # The bot status was changed to administrator.
            elif update["my_chat_member"]["old_chat_member"].get("status") == "member" and \
                    update["my_chat_member"]["new_chat_member"].get("status") == "administrator":
                self.groups[update["my_chat_member"]["chat"]["id"]].update({"bot_admin": True})
                sql.update_chat_in_db(
                    chat_id=update["my_chat_member"]["chat"]["id"],
                    bot_available=self.groups[update["my_chat_member"]["chat"]["id"]]["bot_available"],
                    bot_admin=self.groups[update["my_chat_member"]["chat"]["id"]]["bot_admin"]
                )
                print(update)
                logging.info("update_chat_in_db", self.groups[update["my_chat_member"]["chat"]["id"]])
            # The bot status was changed to member.
            elif update["my_chat_member"]["old_chat_member"].get("status") == "administrator" and \
                    update["my_chat_member"]["new_chat_member"].get("status") == "member":
                self.groups[update["my_chat_member"]["chat"]["id"]].update({"bot_admin": False})
                sql.update_chat_in_db(
                    chat_id=update["my_chat_member"]["chat"]["id"],
                    bot_available=self.groups[update["my_chat_member"]["chat"]["id"]]["bot_available"],
                    bot_admin=self.groups[update["my_chat_member"]["chat"]["id"]]["bot_admin"]
                )
                logging.info("update_chat_in_db", self.groups[update["my_chat_member"]["chat"]["id"]])
        # Log the current event.
        logging.debug("update", update)
        logging.debug(str(self.groups))

    def get_groups(self):
        return self.groups
