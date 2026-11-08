# DineFlow architecture

```text
CustomTkinter role screens
  Customer | Admin | Kitchen | Waiter | Billing
                    ↓
       database.py workflow rules / validation
                    ↓
             SQLite: database/dineflow.db
                    ↓
        report_generator.py → local PDF invoice
```

## ER overview

```text
dining_tables 1 ── * table_sessions 1 ── * orders 1 ── * order_items
                                      └── 1 bills ── 0..1 payments
orders 1 ── 1 kitchen_queue
menu_categories 1 ── * menu_items
```

## Workflow guards

- A reserved or out-of-service table cannot receive a new order.
- Kitchen may only start the oldest waiting order while no other order is preparing.
- An order becomes served only when every one of its item records is checked.
- A bill can be paid once; payment does not release the table.
- Only waiter checkout confirmation closes a paid session and releases the table.
