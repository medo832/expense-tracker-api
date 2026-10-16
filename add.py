import json
from datetime import date, datetime, time
from pathlib import Path

FILE = Path(__file__).parent / "expenser.json"   # always next to add.py, no matter where you run from

# There are many things can bought by humans if it measured by .. Liter , Kg , mg , peac, meter 
# and depend on that this will be our logic as a pre-request of our work 


# ----------------- Ask user for an input and Save it in JSON -------------------

class User:
    def __init__(self, coin_type, unit, proudect, price , quantity, unit_price, date, time):
        self.coin_type = coin_type
        self.unit = unit
        self.proudect = proudect
        self.price = price
        self.quantity = quantity
        self.unit_price = unit_price
        self.date = date
        self.time = time

def main():
    user_data = about_user()

    expense = {

    "coin_type": user_data.coin_type.upper(),
    "unit": user_data.unit,
    "proudect": user_data.proudect.capitalize(), 
    "price": user_data.price,
    "quantity": user_data.quantity,
    "unit_price": user_data.unit_price,
    "date": str(user_data.date),
    "time": str(user_data.time)

    }

    save_expenses(expense)
    my_expenses = view_expenses()

    return expense, my_expenses



def about_user():
    coin_type = input("The coin type is: ")                          # Wabt that in a bar that make use choose the coin type and later want to put it next to any price here
    unit = input("The measurment unit is: ")                         # Want that in a bar that make user choose the unit
    proudect = input("The product is: ")                             # Want that is a space that user write the proudect in it
    price = float(input("The price of prodect is: "))                # Want user to write the price
    quantity = float(input("The quantity is: "))
    unit_price = price / quantity
    now = datetime.now()
    date = now.date()                                                # Date and time are determined automatically by the system
    time = now.time().strftime("%I:%M %p").lower().lstrip("0")
    return User(coin_type, unit, proudect, price, quantity, unit_price, date, time)


def save_expenses(expense):
    try:
        with open(FILE,"r", encoding= "utf-8") as file:
            expenses = json.load(file)
            expenses.append(expense)
    except FileNotFoundError:
        expenses = [expense]
    with open(FILE,"w", encoding= "utf-8") as file:
        json.dump(expenses, file, indent=4)

def view_expenses():
    try:
        with open(FILE,"r", encoding= "utf-8") as file:
            expenses = json.load(file)
            for expense in expenses:
                print(expense)
    except FileNotFoundError:
        print("No expenses found. Please add an expense first.")



if __name__ == "__main__":
    main()

