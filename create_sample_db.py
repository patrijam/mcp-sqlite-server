"""
Create a sample SQLite database for testing the MCP server.
Based on the Table-Augmented-Generation-Exercise referenced in Exercise 4.
"""

import sqlite3
from pathlib import Path

# Create database file
db_path = Path(__file__).parent / "sample_database.db"

# Remove existing database if it exists
if db_path.exists():
    db_path.unlink()

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create customers table
cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT NOT NULL,
        registration_date TEXT NOT NULL
    )
""")

# Create products table
cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        description TEXT
    )
""")

# Create orders table
cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
""")

# Create order_items table
cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
""")

# Insert sample customers
customers_data = [
    ("John", "Doe", "john.doe@email.com", "Switzerland", "2024-01-15"),
    ("Jane", "Smith", "jane.smith@email.com", "Switzerland", "2024-02-20"),
    ("Michael", "Brown", "michael.brown@email.com", "Germany", "2024-03-10"),
    ("Sarah", "Wilson", "sarah.wilson@email.com", "Switzerland", "2024-04-05"),
    ("David", "Lee", "david.lee@email.com", "France", "2024-05-12"),
    ("Emma", "Taylor", "emma.taylor@email.com", "Switzerland", "2024-06-18"),
    ("Oliver", "Anderson", "oliver.anderson@email.com", "Austria", "2024-07-22"),
    ("Sophia", "Martinez", "sophia.martinez@email.com", "Switzerland", "2024-08-30")
]

cursor.executemany("""
    INSERT INTO customers (first_name, last_name, email, country, registration_date)
    VALUES (?, ?, ?, ?, ?)
""", customers_data)

# Insert sample products
products_data = [
    ("Laptop", "Electronics", 1299.99, 15, "High-performance laptop with 16GB RAM"),
    ("Smartphone", "Electronics", 799.99, 30, "Latest model smartphone with advanced camera"),
    ("Desk Chair", "Furniture", 249.99, 20, "Ergonomic office chair with lumbar support"),
    ("Monitor", "Electronics", 399.99, 25, "27-inch 4K monitor"),
    ("Keyboard", "Electronics", 89.99, 50, "Mechanical keyboard with RGB lighting"),
    ("Mouse", "Electronics", 49.99, 60, "Wireless gaming mouse"),
    ("Desk Lamp", "Furniture", 39.99, 40, "LED desk lamp with adjustable brightness"),
    ("Notebook", "Stationery", 12.99, 100, "A4 hardcover notebook"),
    ("Pen Set", "Stationery", 24.99, 80, "Premium ballpoint pen set"),
    ("Headphones", "Electronics", 159.99, 35, "Noise-cancelling wireless headphones")
]

cursor.executemany("""
    INSERT INTO products (product_name, category, price, stock_quantity, description)
    VALUES (?, ?, ?, ?, ?)
""", products_data)

# Insert sample orders
orders_data = [
    (1, "2024-01-20", 1349.98, "Completed"),
    (2, "2024-02-25", 1199.98, "Completed"),
    (1, "2024-03-15", 449.98, "Completed"),
    (4, "2024-04-10", 799.99, "Shipped"),
    (3, "2024-05-20", 1689.97, "Processing"),
    (5, "2024-06-15", 89.99, "Completed"),
    (6, "2024-07-05", 2099.97, "Completed"),
    (8, "2024-08-25", 299.97, "Shipped")
]

cursor.executemany("""
    INSERT INTO orders (customer_id, order_date, total_amount, status)
    VALUES (?, ?, ?, ?)
""", orders_data)

# Insert sample order items
order_items_data = [
    (1, 1, 1, 1299.99),  # Order 1: Laptop
    (1, 6, 1, 49.99),    # Order 1: Mouse
    (2, 2, 1, 1199.99),  # Order 2: Laptop (different price/sale)
    (3, 4, 1, 399.99),   # Order 3: Monitor
    (3, 6, 1, 49.99),    # Order 3: Mouse
    (4, 2, 1, 799.99),   # Order 4: Smartphone
    (5, 1, 1, 1299.99),  # Order 5: Laptop
    (5, 4, 1, 399.99),   # Order 5: Monitor (quantity 1, but represents total)
    (6, 5, 1, 89.99),    # Order 6: Keyboard
    (7, 1, 1, 1299.99),  # Order 7: Laptop
    (7, 2, 1, 799.99),   # Order 7: Smartphone
    (8, 10, 1, 159.99),  # Order 8: Headphones
    (8, 5, 1, 89.99),    # Order 8: Keyboard
    (8, 6, 1, 49.99)     # Order 8: Mouse
]

cursor.executemany("""
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (?, ?, ?, ?)
""", order_items_data)

# Commit and close
conn.commit()
conn.close()

print(f"Sample database created successfully at: {db_path}")
print("\nDatabase Statistics:")
print(f"  - Customers: {len(customers_data)}")
print(f"  - Products: {len(products_data)}")
print(f"  - Orders: {len(orders_data)}")
print(f"  - Order Items: {len(order_items_data)}")
