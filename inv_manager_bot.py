import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import numpy as np
from inventory import Inventory
from math import ceil

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text= help_add + help_remove + help_list)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = ' '.join(context.args)
    text_add = inventory.add(item)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_add)


async def remove_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        print(query.data)
        cmd, item_name, item_amount  = query.data.split(":")
    except IndexError:
        cmd, item_name, item_amount = ["","",""]

    if cmd == "add":
        text_add = inventory.add(item_name, item_amount)
        keyboard = get_inventory_buttons(inventory)
        await get_inline_kb(query, context.bot, keyboard, "Bag of Holding:")
    elif cmd == "remove":
        text_add = inventory.remove(item_name, item_amount)
        keyboard = get_inventory_buttons(inventory)
        await get_inline_kb(query, context.bot, keyboard, "Bag of Holding:")
    elif cmd == "cancel":
        await get_inline_kb(query, context.bot, keyboard, "Bag of Holding:")
    elif cmd == "itemlist":
        keyboard =[[InlineKeyboardButton("ADD", callback_data=f"add:{item_name}:1"), InlineKeyboardButton("REMOVE", callback_data=f"remove:{item_name}:1")],
                    [InlineKeyboardButton("ADD 2", callback_data=f"add:{item_name}:2"), InlineKeyboardButton("REMOVE 2", callback_data=f"remove:{item_name}:2")],
                    [InlineKeyboardButton("ADD 5", callback_data=f"add:{item_name}:5"), InlineKeyboardButton("REMOVE 5", callback_data=f"remove:{item_name}:5")],
                    [InlineKeyboardButton("CANCEL", callback_data="cancel::")]]
        await get_inline_kb(query, context.bot, keyboard, f"EDIT {item_name} x{item_amount}")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_remove = ' '.join(context.args)
    answer_text = inventory.remove(text_remove)


    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=answer_text)

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inventory_buttons = get_inventory_buttons(inventory)

    await update.message.reply_text(reply_markup=InlineKeyboardMarkup(inventory_buttons),
                                    text="Bag of Holding:\n")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Sorry, I didn't understand that command.")

def get_inventory_buttons(inventory):
    inventory_buttons = np.array(
        [InlineKeyboardButton(f"{i}: {item.get_name()} x{item.get_amount()}", callback_data=f"itemlist:{item.get_name()}:") for i, item in enumerate(inventory.get_items())]
        )
    # 2 columns if more than 10 elements
    if len(inventory_buttons) > 10: 
        m, n = 2, ceil(len(inventory_buttons)/2)
    else:
        m, n = 1, len(inventory_buttons)
    inventory_buttons.resize(m, n)
    inventory_buttons = inventory_buttons.T.tolist()

    for arr in inventory_buttons:
        if 0 in arr: arr.remove(0)
    
    return inventory_buttons

async def get_inline_kb(query, bot, keyboard, text):
    await bot.edit_message_text(chat_id=query.message.chat_id,
                                                message_id=query.message.id,
                                                text=f"{text}")
    await bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                                message_id=query.message.id,
                                                reply_markup=InlineKeyboardMarkup(keyboard))


if __name__ == '__main__':
    application = ApplicationBuilder().token('token_here').build()
    
    #start command 
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    #help command 
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    #add command
    add_handler = CommandHandler('add', add)
    application.add_handler(add_handler)

    #remove command
    remove_handler = CommandHandler('remove', remove)
    application.add_handler(remove_handler)

    #list command
    list_handler = CommandHandler({'list','ls'}, list)
    application.add_handler(list_handler)

    #unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    remove_button_handler = CallbackQueryHandler(remove_button)
    application.add_handler(remove_button_handler)
    
    application.run_polling()
