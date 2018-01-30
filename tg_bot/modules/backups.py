import json
from io import BytesIO

from telegram import Bot
from telegram.ext import CommandHandler, run_async

from tg_bot import dispatcher
from tg_bot.__main__ import DATA_IMPORT
from tg_bot.modules.helper_funcs import user_admin


@run_async
@user_admin
def import_data(bot: Bot, update):
    msg = update.effective_message
    chat = update.effective_chat
    # TODO: allow uploading doc with command, not just as reply
    # only work with a doc
    if msg.reply_to_message and msg.reply_to_message.document:
        file_info = bot.get_file(msg.reply_to_message.document.file_id)
        with BytesIO() as file:
            file_info.download(out=file)
            file.seek(0)
            data = json.load(file)

        # only import one group
        if len(data) > 1 and str(chat.id) not in data:
            msg.reply_text("Theres more than one group here in this file, and none have the same chat id as this group "
                           "- how do I choose what to import?")
            return

        # Select data source
        if str(chat.id) in data:
            data = data[str(chat.id)]['hashes']
        else:
            data = data[list(data.keys())[0]]['hashes']

        for mod in DATA_IMPORT:
            mod.__import_data__(str(chat.id), data)

        # TODO: some of that link logic
        # NOTE: consider default permissions stuff?
        msg.reply_text("Backup fully imported. Welcome back! :D")


@run_async
@user_admin
def export_data(bot, update):
    msg = update.effective_message
    msg.reply_text("")


__name__ = "Backups"

__help__ = """
 - /import: reply to a group butler backup file to import as much as possible, making the transfer super simple! Note \
that files/photos can't be imported due to telegram restrictions.
 - /export: !!! This isn't a command yet, but should be coming soon!
"""
IMPORT_HANDLER = CommandHandler("import", import_data)
EXPORT_HANDLER = CommandHandler("export", export_data)

dispatcher.add_handler(IMPORT_HANDLER)
# dispatcher.add_handler(EXPORT_HANDLER)