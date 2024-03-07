from datetime import datetime

from db import DatabaseManager


def create_table_product():
    with DatabaseManager() as cursor:
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                exist BOOLEAN,
                title VARCHAR(150) UNIQUE,
                image VARCHAR(150),
                article VARCHAR(100),
                price_list NUMERIC(10, 2),
                price_in_chain_stores NUMERIC(10, 2),
                price_in_the_online_store NUMERIC(10, 2),
                product_price_of_the_week NUMERIC(10, 2),
                details JSON,
                description TEXT,
                url TEXT,
                category_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  )''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_title_category ON product (title, category_name);''')
        except Exception as e:
            print(f"Error creating table: {e}")


def insert_message(message, timestamp):
    message_date = datetime.utcfromtimestamp(timestamp)
    with DatabaseManager() as cursor:
        cursor.execute("INSERT INTO message (message, time) VALUES (?, ?)", (message, message_date))


def get_messages():
    with DatabaseManager() as cursor:
        cursor.execute("SELECT * FROM message")
        return cursor.fetchall()


def bulk_insert_products(products):
    with DatabaseManager() as cursor:
        try:
            insert_query = '''INSERT INTO product (
                                exist,
                                title,
                                image,
                                article,
                                price_list,
                                price_in_chain_stores,
                                price_in_the_online_store,
                                product_price_of_the_week,
                                details,
                                category_name,
                                description,
                                url,
                                created_at,
                                updated_at) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (title) DO NOTHING;'''
            cursor.executemany(insert_query, [(p['exist'],
                                               p['title'],
                                               p['image'],
                                               p['article'],
                                               p['price_list'],
                                               p['price_in_chain_stores'],
                                               p['price_in_the_online_store'],
                                               p['product_price_of_the_week'],
                                               p['details'],
                                               p['category_name'],
                                               p['description'],
                                               p['url'],
                                               p['created_at'],
                                               p['updated_at']
                                               ) for p in products])
        except Exception as e:
            print(f"Error bulk inserting products: {e}")