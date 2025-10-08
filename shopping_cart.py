# shopping_cart.py
import sys
import copy

# Sample store inventory: item_id -> {name, price, qty}
STORE_INITIAL = {
    1: {"name": "Apple", "price": 20.0, "qty": 50},
    2: {"name": "Banana", "price": 5.0, "qty": 100},
    3: {"name": "Milk (1L)", "price": 45.0, "qty": 20},
    4: {"name": "Bread", "price": 30.0, "qty": 25},
    5: {"name": "Eggs (6 pcs)", "price": 60.0, "qty": 15},
}

DELIVERY_RATES = [
    (15, 50),    # <=15 km => 50 Rs
    (30, 100),   # >15 and <=30 => 100 Rs
]

# TAX_RATE = 0.0

def print_menu():
    print("\nWelcome to the Store — Available Items")
    print("-" * 44)
    print(f"{'ID':<3} {'Item':<18} {'Price(Rs)':>9} {'Stock':>8}")
    print("-" * 44)
    for item_id, info in STORE.items():
        print(f"{item_id:<3} {info['name']:<18} {info['price']:>9.2f} {info['qty']:>8}")
    print("-" * 44)

def get_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            val = int(input(prompt).strip())
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if min_value is not None and val < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and val > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return val

def get_float(prompt, min_value=None, max_value=None):
    while True:
        try:
            val = float(input(prompt).strip())
        except ValueError:
            print("Please enter a valid number.")
            continue
        if min_value is not None and val < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and val > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return val

def choose_items():
    cart = {}  # item_id -> qty
    while True:
        print_menu()
        print("Enter the ID of the item to add to cart (or 0 to finish):")
        item_id = get_int("Item ID: ", min_value=0)
        if item_id == 0:
            break
        if item_id not in STORE:
            print("Invalid item ID. Try again.")
            continue
        store_qty = STORE[item_id]["qty"]
        if store_qty <= 0:
            print(f"Sorry, {STORE[item_id]['name']} is OUT OF STOCK.")
            continue
        max_allowed = store_qty
        qty = get_int(f"Enter quantity (1 to {max_allowed}): ", min_value=1, max_value=max_allowed)
        # add to cart
        cart[item_id] = cart.get(item_id, 0) + qty
        # reduce stock immediately to avoid overselling in same session
        STORE[item_id]["qty"] -= qty
        print(f"Added {qty} x {STORE[item_id]['name']} to cart.")
        # ask if user wants to continue shopping
        cont = input("Add more items? (y/n): ").strip().lower()
        if cont not in ("y", "yes"):
            break
    if not cart:
        print("No items selected.")
    return cart

def get_customer_details():
    print("\n--- Customer Details ---")
    name = input("Full name: ").strip()
    while not name:
        print("Name cannot be empty.")
        name = input("Full name: ").strip()
    phone = input("Phone number: ").strip()
    address = input("Address (for delivery/pickup): ").strip()
    return {"name": name, "phone": phone, "address": address}

def calc_delivery_charge():
    while True:
        dist = get_float("Enter distance from store in km (e.g. 12.5): ", min_value=0.0)
        if dist <= DELIVERY_RATES[0][0]:
            print(f"Delivery available. Charge: Rs {DELIVERY_RATES[0][1]}")
            return DELIVERY_RATES[0][1], dist
        elif dist <= DELIVERY_RATES[1][0]:
            print(f"Delivery available. Charge: Rs {DELIVERY_RATES[1][1]}")
            return DELIVERY_RATES[1][1], dist
        else:
            print("Delivery not available for distances greater than 30 km.")
            choice = input("Choose: (1) Enter another distance  (2) Pickup instead\nSelect 1 or 2: ").strip()
            if choice == "1":
                continue
            else:
                print("You chose pickup. No delivery will be applied.")
                return None, dist  # None signals pickup / no delivery

def print_bill(cart, customer, delivery_charge):
    print("\n" + "="*60)
    print(" " * 20 + "FINAL BILL")
    print("="*60)
    print(f"Customer: {customer['name']}")
    print(f"Phone:    {customer['phone']}")
    print(f"Address:  {customer['address']}")
    print("-"*60)
    print(f"{'Item':<25} {'Qty':>5} {'Price(Rs)':>12} {'Total(Rs)':>12}")
    print("-"*60)
    subtotal = 0.0
    for item_id, qty in cart.items():
        # Note: price should come from initial price (we already reduced store qty)
        # It's safe to use the original STORE price if we hadn't mutated it, but we mutated qty only.
        # Let's fetch name & price from STORE (price unchanged).
        name = STORE[item_id]['name']
        price = STORE[item_id]['price']
        total = price * qty
        subtotal += total
        print(f"{name:<25} {qty:>5} {price:>12.2f} {total:>12.2f}")
    print("-"*60)
    print(f"{'Subtotal':<44} {subtotal:>12.2f}")
    tax = subtotal * TAX_RATE
    if TAX_RATE:
        print(f"{'Tax':<44} {tax:>12.2f}")
    if delivery_charge is None:
        print(f"{'Delivery (pickup)':<44} {0.00:>12.2f}")
        grand_total = subtotal + tax
    else:
        print(f"{'Delivery charge':<44} {delivery_charge:>12.2f}")
        grand_total = subtotal + tax + delivery_charge
    print("="*60)
    print(f"{'GRAND TOTAL (Rs)':<44} {grand_total:>12.2f}")
    print("="*60)
    print("Thank you for shopping with us!")
    print("="*60)


def main():
    # create fresh store copy for each run
    global STORE
    STORE = copy.deepcopy(STORE_INITIAL)
    print("=== Simple Console Shopping Cart ===")
    while True:
        cart = choose_items()
        if not cart:
            print("No purchase made. Exiting.")
            return
        else:
            customer = get_customer_details()
            print("\nDelivery options:")
            delivery_charge, _ = calc_delivery_charge()
            print_bill(cart, customer, delivery_charge)
            # If delivery_charge is None => pickup; otherwise delivery applied
        again = input("Process another customer? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSession cancelled by user. Goodbye.")
        sys.exit(0)

