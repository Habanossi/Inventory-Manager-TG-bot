import numpy as np
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil
import json
import random

def get_inventory_buttons(inventory, msg_id=""):
    inventory_buttons = np.array(
        [InlineKeyboardButton(f"{i}: {item.get_name()} x{item.get_amount()}", callback_data=f"edit:{item.get_name()}:{item.get_amount()}:{msg_id}") for i, item in enumerate(inventory.get_items())]
        )
    # 2 columns if more than 10 elements
    if len(inventory_buttons) > 10:
        m, n = 2, ceil(len(inventory_buttons)/2)
    else:
        m, n = 1, len(inventory_buttons)
    inventory_buttons.resize(m, n)
    inventory_buttons = inventory_buttons.T.tolist()

    for arr in inventory_buttons:
        if 0 in arr:
            arr.remove(0)

    inventory_buttons.append([InlineKeyboardButton("CLOSE", callback_data=f"close:::{msg_id}")])
    return inventory_buttons


async def get_inline_kb(query, bot, keyboard, text):
    await bot.edit_message_text(chat_id=query.message.chat_id,
                                message_id=query.message.id,
                                text=f"{text}")
    await bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                        message_id=query.message.id,
                                        reply_markup=InlineKeyboardMarkup(keyboard))

def get_sticker(username):
    with open("includes/stickers.json", "r") as f:
        data = json.load(f)
    return random.choice(data[username])

def update_pin(update, context, inventory):
    return context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                    message_id=inventory.get_msg_id(),
                                    text=str(inventory))
get_sticker("Flavionator")
