import os.path


class Inventory:
    def __init__(self, inventory_file):
        self.items = []
        self.inventory_file = inventory_file
        if not os.path.exists(self.inventory_file):
            f = open(self.inventory_file, "w")
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
    
    def add(self, item_name, amount=1):
        if item_name == "":
            return "Please enter a valid item to add"
        else:
            # If in items, add amount
            found = False
            for item in self.get_items():
                if str(item.get_name()) == item_name:
                    item.add(amount)
                    found = True

            # If not in items, add to items
            if not found:
                self.items.append(Item(item_name, amount))
            
            self.write_inventory()
            return f"'{item_name}' added to inventory"

    def remove(self, item, amount=1):
        # Option for selecting item by index (int)
        if item.isnumeric():
            try:
                item_name = self.get_items()[int(item)].get_name()
            except IndexError:
                return f"'{item}' is not a valid index"
        else:
            item_name = item

        if item_name == "":
            return "Please enter a valid item to remove"
        # Remove <amount> from Item, if amount becomes < 1 remove the Item from array
        if not self.has_item(item_name):
            return f"'{item_name}' is not in the inventory :("

        for i, curr_item in enumerate(self.get_items()):
            if str(curr_item.get_name()) == item_name:
                curr_item.remove(amount)
                if curr_item.get_amount() < 1:
                    self.items.pop(i)
                self.write_inventory()
                return f"'{item_name}' removed from inventory"

    def write_inventory(self):
        with open(self.inventory_file, "w") as f:
            for curr_item in self.get_items():
                f.write(f"{curr_item.get_name()},{curr_item.get_amount()}\n")


    def has_item(self, item_name):
        found = False
        item_names = [str(item.get_name()) for item in self.get_items()]
        return item_name in item_names
                
    def get_items(self):
        return self.items

class Item:
    def __init__(self, name, amount=1):
        self.name = name
        self.amount = int(amount)
    
    def add(self, amount=1):
        self.amount += int(amount)

    def remove(self, amount=1): 
        self.amount = max(self.amount - int(amount), 0)
    
    # Accessors
    def get_name(self):
        return self.name
    def get_amount(self):
        return self.amount
    def __str__(self):
        return self.get_name()