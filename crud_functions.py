import sqlite3
import asyncio


def initiate_db():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            image_filename TEXT NOT NULL
        )
    ''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON Products (title)")
    for i in range(1, 5):
        cursor.execute("INSERT INTO Products (title, description, price, image_filename) "
                       "VALUES (?, ?, ?, ?)",
                       (f"Продукт{i}", f"Описание{i}", 100 * i, f"{i}.png"))
    connection.commit()
    connection.close()


async def get_all_products():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute("SELECT title, description, price, image_filename FROM Products")
    all_products = cursor.fetchall()
    connection.close()
    return all_products

if __name__ == "__main__":
    initiate_db()
    products = asyncio.run(get_all_products())
    print(products)
