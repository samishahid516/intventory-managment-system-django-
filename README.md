<div align="center">

# 🚲 Inventory Management System

**A full-featured Django inventory management platform with role-based dashboards, real-time stock tracking, and analytics.**

[![Django](https://img.shields.io/badge/Django-6.0.6-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python)](https://python.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## 📋 Overview

This is a **production-ready inventory management system** built for bike shops and small-to-medium retail businesses. It provides separate dashboards for administrators, sales managers, workers, and suppliers — each with tailored functionality.

The system handles the complete lifecycle of inventory management: from product procurement (purchase orders from suppliers) to sales (customer orders) and internal operations (task assignment, issue tracking).

---

## ✨ Features

### 👥 Role-Based Access
| Role | Access |
|------|--------|
| **Admin** | Full system control — user management, reports, settings, all CRUD operations |
| **Sales Manager** | Order management, sales analytics, staff performance tracking |
| **Worker** | Task assignments, issue reporting, product updates |
| **Supplier** | Self-service portal — manage own products and view purchase orders |

### 📦 Inventory Management
- Full **product catalog** with categories, brands, SKU generation
- **Real-time stock tracking** with automatic status updates
- **Low stock alerts** — visual warnings when inventory falls below minimum levels
- **Profit margin calculations** per product (cost vs. selling price)

### 🛒 Sales & Orders
- Create and manage **customer sales orders** with line items
- **Order lifecycle**: Pending → Processing → Shipped → Delivered / Cancelled
- **Payment status** tracking (pending, paid, partial, refunded)
- Automatic **stock deduction** on delivery confirmation
- **Tax calculations** (configurable rate)

### 📊 Analytics & Reporting
- **Dashboard KPIs**: Total revenue, profit, inventory value, low stock counts
- **Sales trends**: Today, weekly, and monthly sales breakdown
- **Profit margin** percentage with cost of goods sold (COGS) calculation
- **Top-selling products** identification

### 🔧 Operations
- **Task management** — assign assembly, servicing, delivery tasks to workers
- **Issue tracking** — report damaged, defective, or missing items
- **Purchase orders** — manage supplier procurement
- **User activity logs** — full audit trail of system actions

### ⚡ Performance
- **Database indexing** on 15+ frequently-queried fields
- **Server-side pagination** on all list views
- **Optimized queries** with `select_related` and `annotate`

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.6, Python 3.14 |
| **Database** | SQLite (dev) / PostgreSQL-ready |
| **Frontend** | Bootstrap 5, jQuery DataTables |
| **Styling** | Custom CSS sidebar layout, responsive design |
| **Auth** | Django Authentication with custom user roles |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/samishahid516/intventory-managment-system-django-.git
cd intventory-managment-system-django-

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# (Optional) Seed the database with realistic demo data
python manage.py seed_data

# Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## 👤 Default Users

The `seed_data` command creates these accounts for testing:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | **Admin** | Full system access |
| `sale_manager` | `manager123` | **Sales Manager** | Order & sales management |
| `worker1` | `worker123` | **Worker** | Task & issue management |
| `worker2` | `worker123` | **Worker** | Task & issue management |
| `worker3` | `worker123` | **Worker** | Task & issue management |
| `supplier1` | `supplier123` | **Supplier** | Self-service product portal |
| `supplier2` | `supplier123` | **Supplier** | Self-service product portal |
| `supplier3` | `supplier123` | **Supplier** | Self-service product portal |

---

## 📂 Project Structure

```
inventory-management/
│
├── accounts/                  # User management & dashboards
│   ├── management/commands/   # Custom management commands
│   │   └── seed_data.py       # Database seeder
│   ├── migrations/
│   ├── models.py              # User, UserActivityLog, SystemSetting
│   ├── views.py               # Dashboard & admin views
│   ├── urls.py                # Route definitions
│   └── decorators.py          # Role-based access decorators
│
├── inventory_system/          # Django project configuration
│   ├── settings.py
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py / asgi.py
│
├── products/                  # Product & category management
│   ├── models.py              # Product, Category models
│   ├── views.py               # CRUD + list views
│   └── urls.py
│
├── sales/                     # Sales order management
│   ├── models.py              # SaleOrder, OrderItem models
│   ├── views.py
│   └── urls.py
│
├── suppliers/                 # Supplier & purchase order management
│   ├── models.py              # Supplier, PurchaseOrder models
│   ├── views.py
│   └── urls.py
│
├── tasks/                     # Task & issue tracking
│   ├── models.py              # Task, Issue models
│   ├── views.py
│   └── urls.py
│
├── static/                    # Static assets
│   └── css/
│       └── sidebar.css        # Custom sidebar layout
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template with sidebar
│   ├── accounts/              # Login, register, profile, admin pages
│   ├── dashboard/             # Role-specific dashboards
│   ├── products/              # Product & category pages
│   ├── sales/                 # Order pages
│   ├── suppliers/             # Supplier pages
│   └── tasks/                 # Task & issue pages
│
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

---

## 🧪 Resetting Demo Data

```bash
python manage.py seed_data
```

This clears all existing data and creates:
- **8 users** across all roles
- **8 product categories**
- **13 products** with realistic pricing
- **4 suppliers** linked to supplier users
- **30 sale orders** with line items
- **10 purchase orders**
- **15 tasks** assigned to workers
- **8 issues** with varying severity
- **50 user activity logs**

---

## 🔧 Configuration

Key settings in `inventory_system/settings.py`:

- **`DATABASES`** — Switch to PostgreSQL by updating the database configuration
- **`TAX_RATE`** — Configurable via SystemSetting model (key: `tax_rate`)
- **`CURRENCY`** — Set via SystemSetting (key: `currency`, default: `PKR`)
- **`TIME_ZONE`** — Currently set to `Asia/Karachi`

---

## 📸 Screenshots

| Dashboard | Products | Orders |
|-----------|----------|--------|
| Role-based KPIs | Card layout with stock status | DataTable with status badges |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  
**Built with ❤️ using Django**

</div>
