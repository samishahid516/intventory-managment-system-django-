# Inventory Management System

A Django-based inventory management system with role-based dashboards for managing bike products, sales orders, suppliers, tasks, and issues.

## Features

- **Role-Based Dashboards**: Admin, Sales Manager, Worker, Supplier — each with tailored views
- **Product Management**: Full CRUD for bikes/products with categories, suppliers, stock tracking
- **Sales Orders**: Create, manage, and track orders through status lifecycle (pending → delivered)
- **Supplier Management**: Manage suppliers and purchase orders
- **Task & Issue Tracking**: Assign tasks to workers, report and resolve issues
- **Stock Alerts**: Low stock and out-of-stock notifications
- **Profit Analytics**: Revenue, COGS, profit margin calculations
- **Search & Pagination**: Server-side pagination and search on list views
- **Database Indexes**: Optimized indexes on frequently-queried fields

## Tech Stack

- **Backend**: Django 6.0.6, Python 3.14
- **Database**: SQLite (development), PostgreSQL-ready
- **Frontend**: Bootstrap 5, jQuery DataTables
- **CSS**: Custom sidebar layout, responsive design

## Installation

```bash
# Clone the repository
git clone https://github.com/samishahid516/intventory-managment-system-django-.git
cd intventory-managment-system-django-

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_data

# Start server
python manage.py runserver
```

## Default Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| sale_manager | manager123 | Sales Manager |
| worker1 | worker123 | Worker |
| worker2 | worker123 | Worker |
| worker3 | worker123 | Worker |
| supplier1 | supplier123 | Supplier |
| supplier2 | supplier123 | Supplier |
| supplier3 | supplier123 | Supplier |

## Usage

Run `python manage.py seed_data` to reset the database with fresh demo data including 13 products, 30 sale orders, 15 tasks, and 8 issues.

## Project Structure

```
├── accounts/          # Users, authentication, dashboards
├── inventory_system/  # Django project settings
├── products/          # Product & category management
├── sales/             # Sale orders & order items
├── suppliers/         # Suppliers & purchase orders
├── tasks/             # Tasks & issue tracking
├── static/            # CSS, JS, images
├── templates/         # HTML templates
└── manage.py          # Django management script
```
