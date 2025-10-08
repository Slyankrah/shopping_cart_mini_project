import psycopg2
from psycopg2.extras import RealDictCursor

# Update these with your DB credentials
DB_HOST = 'localhost'
DB_NAME = 'shopping_cart'
DB_USER = 'admin'
DB_PASSWORD = 'admin123'


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def fetch_all_store_items():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM store ORDER BY item_id")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return items


def update_store_qty(item_id, qty_change):
    """Decrease or increase stock. qty_change can be negative or positive"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE store SET qty = qty + %s WHERE item_id = %s", (qty_change, item_id))
    conn.commit()
    cur.close()
    conn.close()


def save_order(customer, cart, delivery_charge, grand_total):
    conn = get_connection()
    cur = conn.cursor()
    # Insert customer
    cur.execute(
        "INSERT INTO customer (name, phone, address) VALUES (%s,%s,%s) RETURNING customer_id",
        (customer['name'], customer['phone'], customer['address'])
    )
    customer_id = cur.fetchone()[0]

    # Insert order
    cur.execute(
        "INSERT INTO orders (customer_id, delivery_charge, grand_total) VALUES (%s,%s,%s) RETURNING order_id",
        (customer_id, delivery_charge if delivery_charge else 0, grand_total)
    )
    order_id = cur.fetchone()[0]

    # Insert order items
    for item_id, qty in cart.items():
        cur.execute(
            "SELECT price FROM store WHERE item_id = %s",
            (item_id,)
        )
        price = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s,%s,%s,%s)",
            (order_id, item_id, qty, price)
        )
        # Reduce stock
        cur.execute("UPDATE store SET qty = qty - %s WHERE item_id = %s", (qty, item_id))

    conn.commit()
    cur.close()
    conn.close()
