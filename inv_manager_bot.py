import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
f = open("dnd_inventory.txt", "r")
inventory = []
for line in f:
    inventory.append(line.rstrip())
f.close()

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
    f = open("dnd_inventory.txt", "w")
    for item in inventory:
        f.write("%s\n" % item)
    f.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_add + " added to inventory")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_remove = ' '.join(context.args)
    answer_text = text_remove + " removed from inventory"
    try:
        inventory.remove(text_remove)
        f = open("dnd_inventory.txt", "w")
        for item in inventory:
            f.write("%s\n" % item)
        f.close()
    except ValueError:
        answer_text = "No such item in the inventory :("
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_text)

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(inventory)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Listing the contents of the inventory: " + str(', '.join(inventory)) )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

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
    list_handler = CommandHandler('list', list)
    application.add_handler(list_handler)

    #unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    
    application.run_polling()