# DineFlow — Smart Restaurant Operations Management System

DineFlow is a fully offline Windows desktop restaurant-management project built with Python, CustomTkinter and SQLite. It replaces the former MediScan application completely.

## What works

- Customer menu: category browsing, dish search, cart quantities, special instructions, table selection and order placement.
- Shared SQLite workflow: orders open an occupied table session and enter the FIFO kitchen queue automatically.
- Kitchen screen: enforces one active order and oldest-order-first preparation.
- Waiter screen: checks individual items before marking an order delivered; confirms physical checkout only after payment.
- Billing screen: combines all session orders, calculates 5% GST, records Cash/Card/UPI payment, and keeps paid tables occupied until waiter confirmation.
- Admin screen: table floor plan with available, occupied, reserved and out-of-service colours plus live counts.
- Offline PDF invoice helper is available in `report_generator.py` as `generate_invoice(bill_id)`.

## Demonstration accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Kitchen | `kitchen` | `kitchen123` |
| Waiter | `waiter` | `waiter123` |
| Cashier | `cashier` | `cashier123` |

The current demo opens directly to the customer ordering view, with all role areas reachable in the sidebar.

## Run offline

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

The local database is created at `database/dineflow.db`; it includes 12 tables and 14 sample menu items. No APIs, cloud services, or network access are used at runtime.

## Business workflow

```text
Customer order → Table session opens → FIFO kitchen queue
→ Kitchen prepares / marks ready → Waiter checks every item
→ Cashier records payment → Waiter confirms physical checkout
→ Bill closes and table becomes available
```

## Data design

Core persisted tables are `dining_tables`, `table_sessions`, `menu_categories`, `menu_items`, `orders`, `order_items`, `kitchen_queue`, `bills`, `payments`, `reservations`, `users`, and `activity_logs`. Monetary values are stored as integer paise.
