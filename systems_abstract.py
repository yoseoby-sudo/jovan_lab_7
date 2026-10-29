import json
import os
from abc import ABC, abstractmethod

# Interface-style abstract base class for items that can be shipped
class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self):
        # Calculates and returns the shipping cost for the item
        pass


# Abstract base class representing a generic product
class Product(ABC):

    def __init__(self, product_id, name, price, stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._stock = stock

    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def stock(self):
        return self._stock

    def update_stock(self, quantity):
        # Updates the stock quantity securely through a method
        self._stock += quantity

    def display_information(self):
        # Displays formatted common product information
        print(
            f"ID: {self._product_id} | "
            f"Name: {self._name} | "
            f"Price: ${self._price:.2f} | "
            f"Stock: {self._stock}",
            end=" | "
        )

    @abstractmethod
    def get_fulfilment_info(self):
        # Abstract method to define fulfilment details
        pass

    @abstractmethod
    def to_dict(self):
        # Abstract method to convert product to dictionary for JSON persistence
        pass

# Represents a physical product that has weight and requires shipping
class PhysicalProduct(Product, CanBeShipped):

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        self._weight = weight

    @property
    def weight(self):
        return self._weight

    def display_information(self):
        # Overrides parent display_information to include physical attributes
        super().display_information()
        print(f"Weight: {self._weight}kg | Fulfilment: {self.get_fulfilment_info()}")

    def get_fulfilment_info(self):
        return "Requires physical shipping and warehousing."

    def calculate_shipping_cost(self):
        # Example rule: $5 base fee + $2 per kg
        return 5.00 + (self._weight * 2.00)

    def to_dict(self):
        return {
            "type": "physical",
            "id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "weight": self._weight
        }


# Represents a digital product that has a download size
class DigitalProduct(Product):

    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self._download_size = download_size

    @property
    def download_size(self):
        return self._download_size

    def display_information(self):
        # Overrides parent display_information to include digital attributes
        super().display_information()
        print(f"Size: {self._download_size}MB | Fulfilment: {self.get_fulfilment_info()}")

    def get_fulfilment_info(self):
        return "Delivered instantly via download link."

    def to_dict(self):
        return {
            "type": "digital",
            "id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "download_size": self._download_size
        }


#Managing a collection of products and transaction history.
class Inventory:

    def __init__(self):
        self._products = []
        self._transaction_history = []

    #Adds a Product object to the inventory list.
    def add_product(self, product):
        self._products.append(product)

    #Searches for a Product by ID and returns the object, or None if not found.
    def search_product(self, product_id):
        for product in self._products:
            if product.product_id == product_id:
                return product
        return None

    #Displays all products in the inventory.
    def display_all(self):
        print("\nCurrent Inventory")
        print("-" * 64)
        if not self._products:
            print("No products in inventory.")
        else:
            for product in self._products:
                product.display_information()
        print("-" * 64)

    #Records a transaction entry.
    def add_transaction(self, product_id, amount):
        self._transaction_history.append({
            "product_id": product_id,
            "amount": amount
        })

    #Loads inventory data and transaction history from JSON file.
    def load_from_file(self, filename="inventory.json"):
        if os.path.exists(filename):
            print(f"{filename} found.")
            with open(filename, "r") as file:
                data = json.load(file)
            print("Inventory loaded successfully.")

            raw_inventory = data.get("inventory", [])
            self._transaction_history = data.get("transaction_history", [])

            #Convert raw dictionaries from JSON back into Product objects.
            self._products = []
            for item in raw_inventory:
                product = Product(
                    item["id"],
                    item["name"],
                    item["price"],
                    item["stock"]
                )
                self._products.append(product)
        else:
            print(f"{filename} not found. Starting with empty inventory.")
            self._products = []
            self._transaction_history = []
    
    #Saves current inventory and transaction history to JSON file.
    def save_to_file(self, filename="inventory.json"):
        #Convert Product objects into dictionaries using to_dict().
        raw_inventory = [product.to_dict() for product in self._products]
        data = {
            "inventory": raw_inventory,
            "transaction_history": self._transaction_history
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print("Inventory saved successfully!")

#Handles user input and validation for adding a new product.
def handle_add_product(inventory):
    print("\nAdd New Product")

    #Ask for a valid product ID.
    while True:
        product_id_input = input("Product ID: ").strip()
        try:
            product_id = int(product_id_input)
        except ValueError:
            print("Product ID must be a number.")
            continue

        #Check for duplicate product ID using Inventory method.
        if inventory.search_product(product_id) is not None:
            print("Product ID already exists.")
            continue
        break

    #Ask for a valid product name.
    while True:
        product_name = input("Product Name: ").strip()
        if product_name == "":
            print("Product name cannot be empty.")
            continue
        break

    #Ask for a valid product price.
    while True:
        price_input = input("Price: ")
        try:
            price = float(price_input)
        except ValueError:
            print("Price must be a number.")
            continue
        if price < 0:
            print("Price cannot be negative.")
            continue
        break

    #Ask for a valid stock quantity.
    while True:
        stock_input = input("Stock Quantity: ")
        try:
            stock = int(stock_input)
        except ValueError:
            print("Stock quantity must be a number.")
            continue
        if stock < 0:
            print("Stock quantity cannot be negative.")
            continue
        break

    #Create the new Product object and add it to inventory.
    new_product = Product(product_id, product_name, price, stock)
    inventory.add_product(new_product)
    inventory.add_transaction(product_id, stock)

    print("Product added successfully!")


#Handles user input and logic for updating product stock.
def handle_update_stock(inventory):
    product_id_input = input("Product ID: ")
    try:
        product_id = int(product_id_input)
    except ValueError:
        print("Product ID must be a number.")
        return

    product = inventory.search_product(product_id)
    if product:
        quantity_input = input("Stock Quantity to Add: ")
        try:
            quantity = int(quantity_input)
        except ValueError:
            print("Stock quantity must be a number.")
            return

        if quantity < 0:
            print("Stock quantity cannot be negative.")
            return

        #Update stock via the Product object method (Encapsulation).
        product.update_stock(quantity)
        inventory.add_transaction(product_id, quantity)
        print("Stock updated successfully!")
    else:
        print("Product not found.")


#Handles searching for a product by ID and displaying its details.
def handle_search_product(inventory):
    while True:
        product_id_input = input("Product ID to Search: ")
        try:
            product_id = int(product_id_input)
        except ValueError:
            print("Product ID must be a number.")
            continue

        product = inventory.search_product(product_id)
        if product:
            print("\nProduct Found")
            product.display_information()
            break

        print("Product not found.")


def main():
    #Initialize Inventory object and load data.
    inventory = Inventory()
    inventory.load_from_file()

    print("\n=======================================")
    print("        INVENTORY MANAGEMENT SYSTEM")
    print("=======================================")

    #Main menu loop.
    while True:
        print("\n----------- MENU -----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")
        print("----------------------------")

        option = input("Enter option: ")

        if option == "1":
            inventory.display_all()
        elif option == "2":
            handle_add_product(inventory)
        elif option == "3":
            handle_update_stock(inventory)
        elif option == "4":
            handle_search_product(inventory)
        elif option == "5":
            inventory.save_to_file()
        elif option == "6":
            print("Exiting Inventory Management System.")
            break
        else:
            print("Invalid option. Please choose 1-6.")


if __name__ == "__main__":
    main()