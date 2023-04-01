import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

inventory = []
with open("dnd_inventory.txt", "r") as f:
    for line in f:
        inventory.append(line.rstrip())

help_add = "/add <item> adds an item to the inventory.\n"
help_remove = "/remove <item> removes an item from the inventory. If the item cannot be found, it does nothing.\n"
help_list = "/list prints a list of the inventory contents."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, what do you want?")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= help_add + help_remove + help_list)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_add = ' '.join(context.args)
    inventory.append(text_add)
    with open("dnd_inventory.txt", "w") as f:
        for item in inventory:
            f.write("%s\n" % item)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_add + " added to inventory")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text_remove = query.data if query.data else ' '.joint(context.args)

    try:

        if text_remove.isnumeric():
            i = int(text_remove)
            answer_text = inventory[i] + " removed from inventory"
            inventory.pop(i)
        else:
            answer_text = text_remove + " removed from inventory"
            inventory.remove(text_remove)
        with open("dnd_inventory.txt", "w") as f:
            for item in inventory:
                f.write("%s\n" % item)
    except ValueError:
        answer_text = "No such item in the inventory :("
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(item, callback_data=f"{i}")] for i, item in enumerate(inventory)]

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=InlineKeyboardMarkup(buttons),  text="Bag of holding: \n")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token('5645648762:AAEMthbux7lswfGP210SGLTTYqUTiKtOLC4').build()
    
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

    remove_handler = CallbackQueryHandler(remove)
    application.add_handler(remove_handler)
    
    application.run_polling()