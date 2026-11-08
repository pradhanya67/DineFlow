"""SQLite data and workflow rules for the offline DineFlow application."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "database" / "dineflow.db"
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M")
def money(p): return f"₹ {p / 100:,.2f}"
def connection():
    DB_PATH.parent.mkdir(exist_ok=True); c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c

def initialize():
    with connection() as c:
        c.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT,role TEXT,full_name TEXT);
CREATE TABLE IF NOT EXISTS dining_tables(id INTEGER PRIMARY KEY,label TEXT UNIQUE,status TEXT DEFAULT 'AVAILABLE',waiter TEXT,session_id INTEGER);
CREATE TABLE IF NOT EXISTS table_sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,table_id INTEGER,customer_name TEXT,opened_at TEXT,closed_at TEXT,status TEXT DEFAULT 'ACTIVE');
CREATE TABLE IF NOT EXISTS menu_categories(id INTEGER PRIMARY KEY,name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS menu_items(id INTEGER PRIMARY KEY,category_id INTEGER,name TEXT UNIQUE,description TEXT,price_paise INTEGER,prep_minutes INTEGER,image_path TEXT);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,order_no TEXT UNIQUE,session_id INTEGER,status TEXT DEFAULT 'PLACED',notes TEXT,created_at TEXT,started_at TEXT,ready_at TEXT,served_at TEXT);
CREATE TABLE IF NOT EXISTS order_items(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER,menu_item_id INTEGER,item_name TEXT,quantity INTEGER,unit_price_paise INTEGER,served INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS kitchen_queue(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER UNIQUE,position INTEGER,status TEXT DEFAULT 'WAITING');
CREATE TABLE IF NOT EXISTS bills(id INTEGER PRIMARY KEY AUTOINCREMENT,bill_no TEXT UNIQUE,session_id INTEGER UNIQUE,subtotal_paise INTEGER,tax_paise INTEGER,discount_paise INTEGER DEFAULT 0,total_paise INTEGER,status TEXT DEFAULT 'PENDING',created_at TEXT,paid_at TEXT);
CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT,bill_id INTEGER UNIQUE,method TEXT,amount_paise INTEGER,paid_at TEXT);
CREATE TABLE IF NOT EXISTS reservations(id INTEGER PRIMARY KEY AUTOINCREMENT,table_id INTEGER,guest_name TEXT,reserved_at TEXT,status TEXT DEFAULT 'ACTIVE');
CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,message TEXT,logged_at TEXT);
CREATE INDEX IF NOT EXISTS idx_orders_session ON orders(session_id); CREATE INDEX IF NOT EXISTS idx_queue_status ON kitchen_queue(status);
''')
        columns=[x[1] for x in c.execute('PRAGMA table_info(menu_items)')]
        if 'image_path' not in columns: c.execute('ALTER TABLE menu_items ADD COLUMN image_path TEXT')
        if not c.execute('SELECT 1 FROM dining_tables LIMIT 1').fetchone(): seed(c)
        sync_menu(c)

def seed(c):
    c.executemany('INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)',[('admin','admin123','Admin','Aarav Manager'),('kitchen','kitchen123','Kitchen','Chef Riya'),('waiter','waiter123','Waiter','David Waiter'),('cashier','cashier123','Cashier','Nina Cashier')])
    c.executemany('INSERT INTO dining_tables(id,label,status,waiter) VALUES(?,?,?,?)',[(i,f'T{i:02d}','AVAILABLE','David Waiter' if i<7 else 'Maya Waiter') for i in range(1,13)])
    cats=['Starters','Pizza','Burger','Pasta','Mains','Desserts','Beverages']; c.executemany('INSERT INTO menu_categories(id,name) VALUES(?,?)',enumerate(cats,1))
    items=[(1,'Garlic Bread','Toasted garlic bread with herb butter',160,8),(1,'Crispy Corn','Spiced crispy sweet corn',210,10),(2,'Margherita Pizza','Fresh mozzarella, basil and tomato',290,15),(2,'Chicken Tikka Pizza','Tandoori chicken and peppers',390,18),(3,'Chicken Burger','Grilled chicken, lettuce and cheese',240,12),(3,'Veggie Burger','Crisp vegetable patty',180,10),(4,'Pasta Alfredo','Creamy parmesan pasta',340,14),(4,'Arrabbiata Pasta','Tomato, chilli and basil',320,14),(5,'Grilled Chicken','Herb grilled chicken with vegetables',420,18),(5,'Paneer Masala','Paneer in rich tomato gravy',310,16),(6,'Chocolate Cake','Warm chocolate truffle cake',180,7),(6,'Cheesecake','New York style cheesecake',220,7),(7,'Lemon Soda','Fresh lime and soda',90,3),(7,'Cold Coffee','Chilled coffee with ice cream',150,5)]
    c.executemany('INSERT INTO menu_items(category_id,name,description,price_paise,prep_minutes) VALUES(?,?,?,?,?)',items)
def sync_menu(c):
    images={'Crispy Corn':'crispy_corn.jpg','Garlic Bread':'garlic_bread.jpg','Margherita Pizza':'margherita_pizza.jpg','Chicken Tikka Pizza':'chicken_tikka_pizza.jpg','Veggie Burger':'veggie_burger.jpg','Chicken Burger':'chicken_burger.jpg','Arrabbiata Pasta':'arrabbiata_pasta.jpg','Pasta Alfredo':'pasta_alfredo.jpg','Paneer Masala':'paneer_masala.jpg','Grilled Chicken':'grilled_chicken.jpg','Cheesecake':'cheesecake.jpg','Chocolate Cake':'chocolate_cake.jpg','Cold Coffee':'cold_coffee.jpg','Lemon Soda':'lemon_soda.jpg'}
    updates=[('Crispy Corn','Spiced crispy sweet corn',210),('Garlic Bread','Toasted garlic bread with herb butter',160),('Margherita Pizza','Fresh mozzarella, basil and tomato',290),('Chicken Tikka Pizza','Tandoori chicken and peppers',390),('Veggie Burger','Crisp vegetable patty',180),('Chicken Burger','Grilled chicken, lettuce and cheese',240),('Arrabbiata Pasta','Tomato, chilli and basil',320),('Pasta Alfredo','Creamy parmesan pasta',340),('Paneer Masala','Paneer in rich tomato gravy',310),('Grilled Chicken','Herb grilled chicken with vegetables',420),('Cheesecake','New York style cheesecake',220),('Chocolate Cake','Warm chocolate truffle cake',180),('Cold Coffee','Chilled coffee with ice cream',150),('Lemon Soda','Fresh lime and soda',90)]
    for name,description,price in updates:c.execute('UPDATE menu_items SET description=?,price_paise=?,image_path=? WHERE name=?',(description,price*100,images[name],name))
def log(c,msg): c.execute('INSERT INTO activity_logs(message,logged_at) VALUES(?,?)',(msg,now()))
def stats():
    with connection() as c:
        q=lambda s:c.execute(s).fetchone()[0]
        return dict(tables=q('SELECT COUNT(*) FROM dining_tables'),available=q("SELECT COUNT(*) FROM dining_tables WHERE status='AVAILABLE'"),occupied=q("SELECT COUNT(*) FROM dining_tables WHERE status='OCCUPIED'"),reserved=q("SELECT COUNT(*) FROM dining_tables WHERE status='RESERVED'"),active_orders=q("SELECT COUNT(*) FROM orders WHERE status NOT IN ('SERVED','CANCELLED')"),sales=q("SELECT COALESCE(SUM(total_paise),0) FROM bills WHERE status IN ('PAID','CLOSED')"))
def tables():
    with connection() as c:return c.execute('''SELECT t.*,s.customer_name,COALESCE((SELECT COUNT(*) FROM orders o WHERE o.session_id=t.session_id AND o.status NOT IN ('SERVED','CANCELLED')),0) pending,COALESCE((SELECT SUM(oi.quantity*oi.unit_price_paise) FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.session_id=t.session_id),0) total FROM dining_tables t LEFT JOIN table_sessions s ON s.id=t.session_id ORDER BY t.id''').fetchall()
def categories():
    with connection() as c:return ['All']+[r[0] for r in c.execute('SELECT name FROM menu_categories ORDER BY id')]
def menu(category='All',search=''):
    with connection() as c:return c.execute('''SELECT m.*,mc.name category FROM menu_items m JOIN menu_categories mc ON mc.id=m.category_id WHERE (?='All' OR mc.name=?) AND (m.name LIKE ? OR m.description LIKE ?) ORDER BY mc.id,m.name''',(category,category,f'%{search}%',f'%{search}%')).fetchall()
def place_order(table_label,customer,cart,notes=''):
    if not cart: raise ValueError('Add at least one menu item.')
    with connection() as c:
        t=c.execute('SELECT * FROM dining_tables WHERE label=?',(table_label,)).fetchone()
        if not t or t['status'] in ('RESERVED','OUT_OF_SERVICE'): raise ValueError('This table cannot accept an order.')
        sid=t['session_id']
        if not sid:
            sid=c.execute('INSERT INTO table_sessions(table_id,customer_name,opened_at) VALUES(?,?,?)',(t['id'],customer or 'Guest',now())).lastrowid;c.execute("UPDATE dining_tables SET status='OCCUPIED',session_id=? WHERE id=?",(sid,t['id']))
        oid=c.execute("INSERT INTO orders(session_id,notes,created_at) VALUES(?,?,?)",(sid,notes,now())).lastrowid; ono=f'ORD{oid:05d}';c.execute('UPDATE orders SET order_no=? WHERE id=?',(ono,oid))
        for item_id,qty in cart.items():
            m=c.execute('SELECT * FROM menu_items WHERE id=?',(item_id,)).fetchone();c.execute('INSERT INTO order_items(order_id,menu_item_id,item_name,quantity,unit_price_paise) VALUES(?,?,?,?,?)',(oid,item_id,m['name'],qty,m['price_paise']))
        pos=c.execute('SELECT COALESCE(MAX(position),0)+1 FROM kitchen_queue').fetchone()[0];c.execute('INSERT INTO kitchen_queue(order_id,position) VALUES(?,?)',(oid,pos));log(c,f'{ono} placed for {table_label}');return ono
def kitchen_orders(history=False):
    with connection() as c:return c.execute('''SELECT o.*,t.label,GROUP_CONCAT(oi.item_name || ' ×' || oi.quantity, ', ') items,k.status queue_status FROM kitchen_queue k JOIN orders o ON o.id=k.order_id JOIN table_sessions s ON s.id=o.session_id JOIN dining_tables t ON t.id=s.table_id JOIN order_items oi ON oi.order_id=o.id WHERE k.status %s GROUP BY o.id ORDER BY k.position''' % ("IN ('READY','DONE')" if history else "IN ('WAITING','PREPARING')",)).fetchall()
def start_order(order_id):
    with connection() as c:
        if c.execute("SELECT 1 FROM kitchen_queue WHERE status='PREPARING'").fetchone():raise ValueError('Finish the active order before starting another.')
        first=c.execute("SELECT order_id FROM kitchen_queue WHERE status='WAITING' ORDER BY position LIMIT 1").fetchone();q=c.execute('SELECT status FROM kitchen_queue WHERE order_id=?',(order_id,)).fetchone()
        if not q or q[0]!='WAITING' or not first or first[0]!=order_id:raise ValueError('Kitchen must start the oldest waiting order (FIFO).')
        c.execute("UPDATE kitchen_queue SET status='PREPARING' WHERE order_id=?",(order_id,));c.execute("UPDATE orders SET status='PREPARING',started_at=? WHERE id=?",(now(),order_id))
def mark_ready(order_id):
    with connection() as c:
        if not c.execute("SELECT 1 FROM kitchen_queue WHERE order_id=? AND status='PREPARING'",(order_id,)).fetchone():raise ValueError('Only the active order can be marked ready.')
        c.execute("UPDATE kitchen_queue SET status='READY' WHERE order_id=?",(order_id,));c.execute("UPDATE orders SET status='READY',ready_at=? WHERE id=?",(now(),order_id))
def ready_orders():
    with connection() as c:return c.execute('''SELECT o.*,t.label,GROUP_CONCAT(oi.item_name || ' ×' || oi.quantity, ', ') items FROM orders o JOIN table_sessions s ON s.id=o.session_id JOIN dining_tables t ON t.id=s.table_id JOIN order_items oi ON oi.order_id=o.id WHERE o.status='READY' GROUP BY o.id ORDER BY o.ready_at''').fetchall()
def order_items(order_id):
    with connection() as c:return c.execute('SELECT * FROM order_items WHERE order_id=?',(order_id,)).fetchall()
def serve_items(order_id,item_ids):
    with connection() as c:
        c.executemany('UPDATE order_items SET served=1 WHERE id=?',[(x,) for x in item_ids]); left=c.execute('SELECT COUNT(*) FROM order_items WHERE order_id=? AND served=0',(order_id,)).fetchone()[0]
        if left:return False
        c.execute("UPDATE orders SET status='SERVED',served_at=? WHERE id=?",(now(),order_id));c.execute("UPDATE kitchen_queue SET status='DONE' WHERE order_id=?",(order_id,));return True
def bill_for_table(table_label):
    with connection() as c:
        r=c.execute('SELECT session_id FROM dining_tables WHERE label=?',(table_label,)).fetchone()
        if not r or not r[0]:raise ValueError('This table has no active session.')
        sid=r[0];b=c.execute('SELECT * FROM bills WHERE session_id=?',(sid,)).fetchone();sub=c.execute('SELECT COALESCE(SUM(oi.quantity*oi.unit_price_paise),0) FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.session_id=? AND o.status!="CANCELLED"',(sid,)).fetchone()[0];tax=round(sub*.05)
        if not b:
            bid=c.execute('INSERT INTO bills(bill_no,session_id,subtotal_paise,tax_paise,total_paise,created_at) VALUES(?,?,?,?,?,?)',('TMP',sid,sub,tax,sub+tax,now())).lastrowid;c.execute('UPDATE bills SET bill_no=? WHERE id=?',(f'BILL{bid:05d}',bid));b=c.execute('SELECT * FROM bills WHERE id=?',(bid,)).fetchone()
        elif b['status']=='PENDING':c.execute('UPDATE bills SET subtotal_paise=?,tax_paise=?,total_paise=? WHERE id=?',(sub,tax,sub+tax,b['id']));b=c.execute('SELECT * FROM bills WHERE id=?',(b['id'],)).fetchone()
        return b
def bills(status=None):
    with connection() as c:return c.execute('''SELECT b.*,t.label,s.customer_name FROM bills b JOIN table_sessions s ON s.id=b.session_id JOIN dining_tables t ON t.id=s.table_id %s ORDER BY b.id DESC''' % ('WHERE b.status=?' if status else ''),() if not status else (status,)).fetchall()
def bill_items(bill_id):
    with connection() as c:return c.execute('''SELECT oi.item_name,oi.quantity,oi.unit_price_paise FROM bills b JOIN orders o ON o.session_id=b.session_id JOIN order_items oi ON oi.order_id=o.id WHERE b.id=? AND o.status!='CANCELLED' ''',(bill_id,)).fetchall()
def pay_bill(bill_id,method):
    with connection() as c:
        b=c.execute('SELECT * FROM bills WHERE id=?',(bill_id,)).fetchone()
        if not b or b['status']!='PENDING':raise ValueError('This bill is not pending or is already paid.')
        c.execute('INSERT INTO payments(bill_id,method,amount_paise,paid_at) VALUES(?,?,?,?)',(bill_id,method,b['total_paise'],now()));c.execute("UPDATE bills SET status='PAID',paid_at=? WHERE id=?",(now(),bill_id));log(c,f'{b["bill_no"]} paid by {method}')
def confirm_checkout(table_label):
    with connection() as c:
        t=c.execute('SELECT * FROM dining_tables WHERE label=?',(table_label,)).fetchone()
        if not t or not t['session_id']:raise ValueError('No active customer session.')
        b=c.execute('SELECT * FROM bills WHERE session_id=?',(t['session_id'],)).fetchone()
        if not b or b['status']!='PAID':raise ValueError('Payment must be recorded before checkout confirmation.')
        c.execute("UPDATE bills SET status='CLOSED' WHERE id=?",(b['id'],));c.execute("UPDATE table_sessions SET status='CLOSED',closed_at=? WHERE id=?",(now(),t['session_id']));c.execute("UPDATE dining_tables SET status='AVAILABLE',session_id=NULL WHERE id=?",(t['id'],));log(c,f'{table_label} checkout confirmed and released')
