import asyncio
import copy
import json
import typing
from aiogram import Bot, Dispatcher
from aiohttp.helpers import sentinel
import aiohttp
import logging
from aiogram.utils.mixins import DataMixin, ContextInstanceMixin
import sql

T = typing.TypeVar('T')


class OptimizedDispatcher(Dispatcher):
    def __init__(self, bot):
        # This dict will hold the groups where the bot was added.
        # The key will be the id of the group, the value will hold
        # boolean values that indicates whether the bot is added or removed
        # or whether the bot is an admin or not.
        self.groups = sql.get_chats_dict_from_db()
        super().__init__(bot)

    def get_groups(self):
        return self.groups
    async def start_polling(self,
                            timeout=20,
                            relax=0.1,
                            limit=None,
                            reset_webhook=None,
                            fast: bool = True,
                            error_sleep: int = 5,
                            allowed_updates: typing.Optional[typing.List[str]] = None):

        """
        Start long-polling. This is a modified version of start_polling() that tracks
        if a bot gets added to a supergroup.

        :param timeout:
        :param relax:
        :param limit:
        :param reset_webhook:
        :param fast:
        :param error_sleep:
        :param allowed_updates:
        :return:
        """
        if self._polling:
            raise RuntimeError('Polling already started')

        logging.info('Start polling.')

        # context.set_value(MODE, LONG_POLLING)
        Dispatcher.set_current(self)
        Bot.set_current(self.bot)

        if reset_webhook is None:
            await self.reset_webhook(check=False)
        if reset_webhook:
            await self.reset_webhook(check=True)

        self._polling = True
        offset = None
        try:
            current_request_timeout = self.bot.timeout
            if current_request_timeout is not sentinel and timeout is not None:
                request_timeout = aiohttp.ClientTimeout(total=current_request_timeout.total + timeout or 1)
            else:
                request_timeout = None

            while self._polling:
                try:
                    with self.bot.request_timeout(request_timeout):
                        updates = await self.bot.get_updates(
                            limit=limit,
                            offset=offset,
                            timeout=timeout,
                            allowed_updates=allowed_updates
                        )
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logging.exception('Cause exception while getting updates.')
                    await asyncio.sleep(error_sleep)
                    continue
                finally:
                    if updates:
                        updates_dict: dict = json.loads(updates[0].__str__())
                        if updates_dict.get("my_chat_member"):
                            # The bot was added to the supergroup.
                            if updates_dict["my_chat_member"]["old_chat_member"]["status"] == "left" and \
                                updates_dict["my_chat_member"]["new_chat_member"]["status"] == "member":
                                self.groups[updates_dict["my_chat_member"]["chat"]["id"]] = {
                                    "chat": copy.deepcopy(updates_dict["my_chat_member"]["chat"]),
                                    "bot_available": True,
                                    "bot_admin": False
                                }
                                sql.add_chat_to_db(
                                    {
                                        "id": updates_dict["my_chat_member"]["chat"]["id"],
                                        "chat_title": updates_dict["my_chat_member"]["chat"]["title"],
                                        "chat_type": updates_dict["my_chat_member"]["chat"]["type"],
                                        "bot_available": True,
                                        "bot_admin": False
                                    }
                                )
                            # the bot was removed from the supergroup.
                            elif updates_dict["my_chat_member"]["old_chat_member"]["status"] == "member" and \
                                updates_dict["my_chat_member"]["new_chat_member"]["status"] == "left":
                                if self.groups.get(updates_dict["my_chat_member"]["chat"]["id"]):
                                    self.groups[updates_dict["my_chat_member"]["chat"]["id"]].update(
                                        {"bot_available": False}
                                    )
                                    sql.delete_chat_from_db(id=updates_dict["my_chat_member"]["chat"]["id"])
                            # The bot status was changed to administrator.
                            elif updates_dict["my_chat_member"]["old_chat_member"].get("status") == "member" and \
                                updates_dict["my_chat_member"]["new_chat_member"].get("status") == "administrator":
                                self.groups[updates_dict["my_chat_member"]["chat"]["id"]].update({"bot_admin": True})
                                sql.update_chat_in_db(
                                    id=updates_dict["my_chat_member"]["chat"]["id"],
                                    bot_available=self.groups[updates_dict["my_chat_member"]["chat"]["id"]]["bot_available"],
                                    bot_admin=self.groups[updates_dict["my_chat_member"]["chat"]["id"]]["bot_admin"]
                                )
                            # The bot status was changed to member.
                            elif updates_dict["my_chat_member"]["old_chat_member"].get("status") == "administrator" and \
                                updates_dict["my_chat_member"]["new_chat_member"].get("status") == "member":
                                self.groups[updates_dict["my_chat_member"]["chat"]["id"]].update({"bot_admin": False})
                                sql.update_chat_in_db(
                                    id=updates_dict["my_chat_member"]["chat"]["id"],
                                    bot_available=self.groups[updates_dict["my_chat_member"]["chat"]["id"]]["bot_available"],
                                    bot_admin=self.groups[updates_dict["my_chat_member"]["chat"]["id"]]["bot_admin"]
                                )
                        else:
                            # Log the current event.
                            logging.debug(json.dumps(updates_dict, indent=4))
                    else:
                        # Log the full data about the bot groups.
                        logging.debug(json.dumps(self.groups, indent=4))

                if updates:
                    logging.debug(f"Received {len(updates)} updates.")
                    offset = updates[-1].update_id + 1

                    asyncio.create_task(self._process_polling_updates(updates, fast))

                if relax:
                    await asyncio.sleep(relax)

        finally:
            self._close_waiter.set_result(None)
            logging.warning('Polling is stopped.')

