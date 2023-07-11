import os.path
from includes.helpers import logging

class Inventory:
    def __init__(self, inventory_file):
        logging.info("Started bot")
        self.items = []
        self.inventory_file = inventory_file
        self.pin_file = "./includes/pin_msg_id.txt"
        self.msg_id = ""

        if not os.path.exists(self.inventory_file):
            f = open(self.inventory_file, "w+")
            f.close()
        if not os.path.exists(self.pin_file):
            f = open(self.pin_file, "w+")
            f.close()

        with open(self.inventory_file, "r") as f:
            for line in f:
                line_split = line.split(",")
                item_name = line_split[0]
                try:
                    item_amount = line_split[1]
                except IndexError:
                    item_amount = 1
                self.items.append(Item(item_name.strip(), item_amount))
        with open(self.pin_file, "r") as f:
            self.msg_id = f.read()
            print("MESSAGE_ID: ", self.msg_id)

    def __contains__(self, item_name):
        return item_name in [item.name for item in self.items]

    def __str__(self):
        s = "Bag of Holding:\n"
        for item in self.items:
            s += f"\t{item.name}: x{item.amount}\n"
        return s

    def add(self, item_name, amount=1):
        if item_name == "":
            logging.info("Tried to add item with no name.")
            return "Please enter a valid item to add"
        else:
            # If in items, increment amount
            if item_name in self:
                for item in self.items:
                    if str(item.name) == item_name:
                        #item.increment(amount)
                        item += amount
                        found = True
            else:
                self.items.append(Item(item_name, amount))

            self.write_inventory()
            return f"'{item_name}' added to Inventory"

    def remove(self, input, amount=1):
        # Option for selecting item by index (int)
        if input.isnumeric():
            try:
                index = input
                item_name = self.items[int(index)].name
            except IndexError:
                return f"'{index}' is not a valid index"
        else:
            item_name = input

        if item_name == "":
            logging.info("Tried to remove item with no name")
            return "Please enter a valid item to remove"
        # Remove <amount> from Item, if amount becomes < 1 remove the Item from array
        if not self.has_item(item_name):
            logging.info(f"Tried to remove item {item_name}, which is not in the Inventory")
            return f"'{item_name}' is not in the inventory :("

        for i, curr_item in enumerate(self.items):
            if str(curr_item.name) == item_name:
                curr_item -= amount
                if curr_item.amount < 1:
                    self.items.pop(i)
                self.write_inventory()
                return f"'{item_name}' removed from inventory"

    def write_inventory(self):
        with open(self.inventory_file, "w") as f:
            for curr_item in self.items:
                f.write(f"{curr_item.name},{curr_item.amount}\n")

    def has_item(self, item_name):
        item_names = [str(item.name) for item in self.items]
        return item_name in item_names

    def set_msg_id(self, id):
        self.msg_id = str(id)
        with open(self.pin_file, "w") as f:
            f.write(self.msg_id)

    def get_msg_id(self):
        return self.msg_id

class Item:
    def __init__(self, name, amount=1):
        self.name = name
        self.amount = int(amount)

    def __iadd__(self, amount=1):
        self.amount += int(amount)
        return self

    def __isub__(self, amount=1):
        self.amount = max(self.amount - int(amount), 0)
        return self

    def __str__(self):
        return self.name
