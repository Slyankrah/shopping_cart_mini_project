import sys
from db import fetch_all_store_items, update_store_qty, save_order
from decimal import Decimal

DELIVERY_RATES = [
    (15, 50),    # <=15 km => 50 Rs
    (30, 100),   # >15 and <=30 => 100 Rs
]


def print_menu(store):
    print("\nWelcome to the Store — Available Items")
    print("-" * 44)
    print(f"{'ID':<3} {'Item':<18} {'Price(Rs)':>9} {'Stock':>8}")
    print("-" * 44)
    for item_id, info in store.items():
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


def print_cart(cart, store):
    if not cart:
        print("\nCart is empty.")
        return
    print("\nCurrent Cart:")
    print("-" * 60)
    print(f"{'ID':<3} {'Item':<25} {'Qty':>5} {'Price':>9} {'Total':>10}")
    print("-" * 60)
    subtotal = Decimal('0.00')
    for item_id, qty in cart.items():
        name = store[item_id]['name']
        price = store[item_id]['price']
        total = price * qty
        subtotal += total
        print(f"{item_id:<3} {name:<25} {qty:>5} {price:>9.2f} {total:>10.2f}")
    print("-" * 60)
    print(f"{'Subtotal':<44} {subtotal:>12.2f}")


def choose_items(cart=None, store=None):
    if cart is None:
        cart = {}
    while True:
        print_menu(store)
        print("Enter the ID of the item to add to cart (or 0 to finish):")
        item_id = get_int("Item ID: ", min_value=0)
        if item_id == 0:
            break
        if item_id not in store:
            print("Invalid item ID. Try again.")
            continue
        store_qty = store[item_id]["qty"]
        if store_qty <= 0:
            print(f"Sorry, {store[item_id]['name']} is OUT OF STOCK.")
            continue
        max_allowed = store_qty
        qty = get_int(f"Enter quantity (1 to {max_allowed}): ", min_value=1, max_value=max_allowed)
        # add to cart and reduce stock in store dict
        cart[item_id] = cart.get(item_id, 0) + qty
        store[item_id]["qty"] -= qty
        print(f"Added {qty} x {store[item_id]['name']} to cart.")
        cont = input("Add more items? (y/n): ").strip().lower()
        while cont not in ("y", "yes", "n", "no"):
            print("Invalid input. Try again.")
            cont = input("Add more items? (y/n): ").strip().lower()
        if cont not in ("y", "yes"):
            break
    if not cart:
        print("No items selected.")
    return cart


def edit_cart(cart, store):
    if not cart:
        print("Cart is empty. Nothing to edit.")
        return cart
    print_cart(cart, store)
    item_id = get_int("Enter the item ID to edit (0 to cancel): ", min_value=0)
    if item_id == 0 or item_id not in cart:
        return cart
    current_qty = cart[item_id]
    available_for_increase = store[item_id]["qty"] + current_qty
    new_qty = get_int(
        f"Enter new quantity for {store[item_id]['name']} (0 to remove, max {available_for_increase}): ",
        min_value=0, max_value=available_for_increase
    )
    if new_qty == current_qty:
        print("Quantity unchanged.")
        return cart
    if new_qty == 0:
        del cart[item_id]
        store[item_id]["qty"] += current_qty
        print(f"Removed {store[item_id]['name']} from cart.")
    elif new_qty > current_qty:
        delta = new_qty - current_qty
        cart[item_id] = new_qty
        store[item_id]["qty"] -= delta
        print(f"Increased {store[item_id]['name']} to {new_qty}.")
    else:
        delta = current_qty - new_qty
        cart[item_id] = new_qty
        store[item_id]["qty"] += delta
        print(f"Decreased {store[item_id]['name']} to {new_qty}.")
    return cart


def remove_from_cart(cart, store):
    if not cart:
        print("Cart is empty. Nothing to remove.")
        return cart
    print_cart(cart, store)
    item_id = get_int("Enter the item ID to remove (0 to cancel): ", min_value=0)
    if item_id == 0 or item_id not in cart:
        return cart
    qty = cart[item_id]
    del cart[item_id]
    store[item_id]["qty"] += qty
    print(f"Removed {qty} x {store[item_id]['name']} from cart.")
    return cart


def get_customer_details():
    print("\n--- Customer Details ---")
    name = input("Full name: ").strip()
    while not name:
        print("Name cannot be empty.")
        name = input("Full name: ").strip()
    phone = input("Phone number: ").strip()
    return {"name": name, "phone": phone}


def get_delivery_address():
    address = input("Address (for delivery/pickup): ").strip()
    if not address:
        address = ""
    return {"address": address}


def choose_delivery_method():
    while True:
        print("\nDelivery options:")
        print("1) Delivery")
        print("2) Pickup")
        choice = input("Select 1 for Delivery or 2 for Pickup: ").strip()
        if choice == "1":
            return "delivery"
        elif choice == "2":
            return "pickup"
        else:
            print("Invalid choice. Please select 1 or 2.")


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
                return None, dist


def print_bill(cart, customer, delivery_charge, store):
    if "address" not in customer:
        customer["address"] = ""
    print("\n" + "=" * 60)
    print(" " * 20 + "FINAL BILL")
    print("=" * 60)
    print(f"Customer: {customer['name']}")
    print(f"Phone:    {customer['phone']}")
    print(f"Address:  {customer['address']}")
    print("-" * 60)
    print(f"{'Item':<25} {'Qty':>5} {'Price(Rs)':>12} {'Total(Rs)':>12}")
    print("-" * 60)
    subtotal = Decimal('0.00')
    for item_id, qty in cart.items():
        name = store[item_id]['name']
        price = store[item_id]['price']
        total = price * qty
        subtotal += total
        print(f"{name:<25} {qty:>5} {price:>12.2f} {total:>12.2f}")
    print("-" * 60)
    print(f"{'Subtotal':<44} {subtotal:>12.2f}")
    if delivery_charge is None:
        print(f"{'Delivery (pickup)':<44} {0.00:>12.2f}")
        grand_total = subtotal
    else:
        print(f"{'Delivery charge':<44} {delivery_charge:>12.2f}")
        grand_total = subtotal + delivery_charge
    print("=" * 60)
    print(f"{'GRAND TOTAL (Rs)':<44} {grand_total:>12.2f}")
    print("=" * 60)
    print("Thank you for shopping with us!")
    print("=" * 60)
    return grand_total


def manage_cart_before_checkout(cart, store):
    while True:
        if not cart:
            print("\nYour cart is empty. Please add items before checkout.")
            cart = choose_items(cart, store)
            if not cart:
                print("No items added. Cancelling order.")
                return "cancel", {}
            continue

        print_cart(cart, store)
        print("\nCart options:")
        print("1) Proceed to checkout")
        print("2) Edit item quantity")
        print("3) Remove item")
        print("4) Add more items")
        print("5) Cancel order")
        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            return "checkout", cart
        elif choice == "2":
            cart = edit_cart(cart, store)
        elif choice == "3":
            cart = remove_from_cart(cart, store)
        elif choice == "4":
            cart = choose_items(cart, store)
        elif choice == "5":
            for item_id, qty in list(cart.items()):
                store[item_id]["qty"] += qty
            return "cancel", {}
        else:
            print("Invalid option. Please enter a number between 1 and 5.")


def main():
    print("=== Simple Console Shopping Cart ===")
    while True:
        store = fetch_all_store_items()
        store = {item['item_id']: item for item in store}  # convert list to dict
        cart = choose_items(store=store)
        if not cart:
            print("No purchase made. Exiting.")
            return

        action, cart = manage_cart_before_checkout(cart, store)
        if action == "cancel":
            print("Order cancelled.")
            again = input("Process another customer? (y/n): ").strip().lower()
            if again not in ("y", "yes"):
                break
            else:
                continue

        customer = get_customer_details()
        method = choose_delivery_method()
        if method == "delivery":
            customer.update(get_delivery_address())
            delivery_charge, _ = calc_delivery_charge()
            if delivery_charge is None:
                method = "pickup"
        else:
            customer["address"] = "Pickup - collect at store"
            delivery_charge = None
            print("Pickup selected. No delivery charge will be applied.")

        grand_total = print_bill(cart, customer, delivery_charge, store)
        save_order(customer, cart, delivery_charge, grand_total)
        print("Order saved to database!")

        again = input("Process another customer? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSession cancelled by user. Goodbye.")
        sys.exit(0)