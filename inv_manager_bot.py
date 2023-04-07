import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from inventory import Inventory
from bot_token import token
from includes.helpers import get_inventory_buttons, get_inline_kb

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

inventory_file = "dnd_inventory.txt"
inventory = Inventory(inventory_file)

help_add = "/add <item> adds an item to the inventory.\n"
help_remove = "/remove <item/index> removes an item from the inventory. If the item cannot be found, it does nothing.\n"
help_list = "/list prints a list of the inventory contents."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, what do you want?")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_add + help_remove + help_list)

    logging.info(f"{update.message.from_user.first_name} needed help")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = ' '.join(context.args)
    text_add = inventory.add(item)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_add)


async def remove_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        cmd, item_name, item_amount, msg_id = query.data.split(":")
    except IndexError:
        cmd, item_name, item_amount, msg_id = ["", "", "", ""]

    if cmd == "add":
        inventory.add(item_name, item_amount)
        await get_inline_kb(query, context.bot, get_inventory_buttons(inventory, msg_id), "Bag of Holding:")
        logging.info(f"{query.message.from_user.first_name} added {item_amount} of {item_name} - {msg_id}")
    elif cmd == "remove":
        inventory.remove(item_name, item_amount)
        await get_inline_kb(query, context.bot, get_inventory_buttons(inventory, msg_id), "Bag of Holding:")
        logging.info(f"{query.message.from_user.first_name} removed {item_amount} of {item_name} - {msg_id}")
    elif cmd == "cancel":
        await get_inline_kb(query, context.bot, get_inventory_buttons(inventory, msg_id), "Bag of Holding:")
        logging.info(f"{query.message.from_user.first_name} canceled edit screen")
    elif cmd == "close":
        sticker_id = 'CAACAgQAAxkBAAIBsGQwiKNjerbplYTqG8-jZ9hHJBSlAAKLDQACftTxUtY7qzVqXQABVS8E'
        await query.message.delete()
        await context.bot.send_sticker(chat_id=update.effective_chat.id,
                                       sticker=sticker_id,)
        # await context.bot.delete_message(chat_id=query.message.chat_id,
        #                                  message_id=msg_id)
        logging.info(f"{query.message.from_user.first_name} closed inline keyboard message")
    elif cmd == "edit":
        keyboard = [[InlineKeyboardButton("ADD", callback_data=f"add:{item_name}:1:{msg_id}"), InlineKeyboardButton("REMOVE", callback_data=f"remove:{item_name}:1:{msg_id}")],
                    [InlineKeyboardButton("ADD 2", callback_data=f"add:{item_name}:2:{msg_id}"), InlineKeyboardButton("REMOVE 2", callback_data=f"remove:{item_name}:2:{msg_id}")],
                    [InlineKeyboardButton("ADD 5", callback_data=f"add:{item_name}:5:{msg_id}"), InlineKeyboardButton("REMOVE 5", callback_data=f"remove:{item_name}:5:{msg_id}")],
                    [InlineKeyboardButton("CANCEL", callback_data=f"cancel:::{msg_id}")]]
        await get_inline_kb(query, context.bot, keyboard, f"EDIT {item_name} x{item_amount}")
        logging.info(f"{query.message.from_user.first_name} wants to edit {item_name} - {msg_id}")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text_remove = ' '.join(context.args)
    answer_text = inventory.remove(text_remove)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=answer_text)

    logging.info(f"{update.message.from_user.first_name} removed {text_remove} - response: {answer_text}")


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inventory_buttons = get_inventory_buttons(inventory, update.message.id)

    await update.message.reply_text(reply_markup=InlineKeyboardMarkup(inventory_buttons),
                                    text="Bag of Holding:\n")

    logging.info(f"{update.message.from_user.first_name} had a peak in the Bag of Holding: {str(inventory)}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Sorry, I didn't understand that command.")

    logging.info(f"{update.message.from_user.first_name} said an unknown command")


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    # start command
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # help command
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    # add command
    add_handler = CommandHandler('add', add)
    application.add_handler(add_handler)

    # remove command
    remove_handler = CommandHandler('remove', remove)
    application.add_handler(remove_handler)

    # list command
    list_handler = CommandHandler({'list', 'ls'}, list)
    application.add_handler(list_handler)

    # unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    remove_button_handler = CallbackQueryHandler(remove_button)
    application.add_handler(remove_button_handler)

    application.run_polling()
