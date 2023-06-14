import sqlite3 as sq


async def db_start():
    global db, cur
    db = sq.connect('tg.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "cart_id TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT,"
                "desc TEXT, "
                "price TEXT, "
                "photo TEXT, "
                "count INTEGER, "
                "brand TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS carts("
                "c_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "items TEXT)")
    db.commit()


async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        db.commit()


async def add_item(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, count, photo, brand) VALUES (?, ?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['count'], data['photo'], data['type']))
        db.commit()

async def add_to_cart(user_id, items):
        item_list = cur.execute("SELECT items FROM carts WHERE user_id == {key}".format(key=user_id)).fetchone()
        if not item_list:
            cur.execute("INSERT INTO carts (user_id, items) VALUES (?, ?)", (user_id, items))
            db.commit()
        else:
            cur.execute("UPDATE carts SET items = (?) WHERE user_id == (?)", (item_list[0] + '|' + items, user_id))
            db.commit()

async def get_items(type):
        items = cur.execute("SELECT * FROM items WHERE brand == '{key}' AND count > 0".format(key=type)).fetchall()
        return items

async def get_item(type, id):
        items = cur.execute("SELECT * FROM items WHERE brand == '{key1}' AND i_id == {key2}".format(key1=type, key2=id)).fetchall()
        #items = cur.execute("SELECT * FROM items WHERE brand == '{type}' AND i_id == {id}").fetchall()
        return items

async def get_cart(id):
        cart = cur.execute("SELECT * FROM carts WHERE user_id == {key}".format(key=id)).fetchall()
        return cart

async def remove_cart(id):
        cur.execute("DELETE FROM carts WHERE user_id == {key}".format(key=id))
        db.commit()


