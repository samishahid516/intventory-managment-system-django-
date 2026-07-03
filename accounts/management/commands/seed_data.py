from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data'

    def handle(self, *args, **options):
        from accounts.models import User, UserActivityLog, SystemSetting
        from products.models import Category, Product
        from suppliers.models import Supplier, PurchaseOrder
        from sales.models import SaleOrder, OrderItem
        from tasks.models import Task, Issue

        self.stdout.write('Clearing existing data...')
        Issue.objects.all().delete()
        Task.objects.all().delete()
        OrderItem.objects.all().delete()
        SaleOrder.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        Product.objects.all().delete()
        Supplier.objects.all().delete()
        Category.objects.all().delete()
        UserActivityLog.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        SystemSetting.objects.all().delete()

        now = timezone.now()

        # === USERS ===
        users_data = [
            {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'is_staff': True, 'email': 'admin@inventory.com'},
            {'username': 'sale_manager', 'password': 'manager123', 'role': 'sale_manager', 'email': 'manager@inventory.com'},
            {'username': 'worker1', 'password': 'worker123', 'role': 'worker', 'email': 'worker1@inventory.com'},
            {'username': 'worker2', 'password': 'worker123', 'role': 'worker', 'email': 'worker2@inventory.com'},
            {'username': 'worker3', 'password': 'worker123', 'role': 'worker', 'email': 'worker3@inventory.com'},
            {'username': 'supplier1', 'password': 'supplier123', 'role': 'supplier', 'email': 'supplier1@inventory.com'},
            {'username': 'supplier2', 'password': 'supplier123', 'role': 'supplier', 'email': 'supplier2@inventory.com'},
            {'username': 'supplier3', 'password': 'supplier123', 'role': 'supplier', 'email': 'supplier3@inventory.com'},
        ]
        users = {}
        for data in users_data:
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                password=make_password(data['password']),
                role=data['role'],
                is_staff=data.get('is_staff', False),
                is_active=True,
            )
            users[data['username']] = user
            self.stdout.write(f'  Created user: {user.username} ({user.role})')

        # === SYSTEM SETTINGS ===
        SystemSetting.objects.create(key='company_name', value='Inventory Management System')
        SystemSetting.objects.create(key='company_address', value='123 Main Street, Lahore, Pakistan')
        SystemSetting.objects.create(key='company_phone', value='+92-300-1234567')
        SystemSetting.objects.create(key='company_email', value='info@inventory.com')
        SystemSetting.objects.create(key='currency', value='PKR')
        SystemSetting.objects.create(key='tax_rate', value='13.00')

        # === CATEGORIES ===
        cat_data = [
            'Road Bikes', 'Mountain Bikes', 'BMX Bikes', 'Electric Bikes',
            'Hybrid Bikes', 'Kids Bikes', 'Folding Bikes', 'Cruiser Bikes',
        ]
        categories = {}
        for name in cat_data:
            cat = Category.objects.create(name=name)
            categories[name] = cat
        self.stdout.write(f'  Created {len(cat_data)} categories')

        # === SUPPLIERS ===
        supplier_data = [
            {'name': 'Atlas Honda', 'email': 'info@atlashonda.pk', 'phone': '042-111-333-333', 'city': 'Lahore', 'user': 'supplier1'},
            {'name': 'Yamaha Motors', 'email': 'info@yamaha.pk', 'phone': '021-111-444-444', 'city': 'Karachi', 'user': 'supplier2'},
            {'name': 'United Spare Parts', 'email': 'info@united.pk', 'phone': '042-111-555-555', 'city': 'Lahore', 'user': 'supplier3'},
            {'name': 'Premium Bike Suppliers', 'email': 'info@premiumbikes.pk', 'phone': '051-111-666-666', 'city': 'Islamabad', 'user': None},
        ]
        suppliers = {}
        for data in supplier_data:
            supplier = Supplier.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                city=data['city'],
                is_active=True,
                user=users.get(data['user']),
            )
            suppliers[data['name']] = supplier
        self.stdout.write(f'  Created {len(supplier_data)} suppliers')

        # === PRODUCTS ===
        products_data = [
            {'name': 'Speedster Road Bike', 'category': 'Road Bikes', 'supplier': 'Atlas Honda', 'price': 45000, 'cost_price': 35000, 'quantity': 15, 'min_stock': 5, 'brand': 'Atlas', 'status': 'available'},
            {'name': 'Racer X Road Bike', 'category': 'Road Bikes', 'supplier': 'Yamaha Motors', 'price': 55000, 'cost_price': 42000, 'quantity': 10, 'min_stock': 5, 'brand': 'Yamaha', 'status': 'available'},
            {'name': 'Trail Blazer Mountain Bike', 'category': 'Mountain Bikes', 'supplier': 'Atlas Honda', 'price': 65000, 'cost_price': 48000, 'quantity': 8, 'min_stock': 5, 'brand': 'Atlas', 'status': 'available'},
            {'name': 'Mountain King Pro', 'category': 'Mountain Bikes', 'supplier': 'Yamaha Motors', 'price': 85000, 'cost_price': 62000, 'quantity': 5, 'min_stock': 3, 'brand': 'Yamaha', 'status': 'available'},
            {'name': 'BMX Stunt Pro', 'category': 'BMX Bikes', 'supplier': 'United Spare Parts', 'price': 25000, 'cost_price': 18000, 'quantity': 20, 'min_stock': 5, 'brand': 'United', 'status': 'available'},
            {'name': 'City Cruiser Comfort Bike', 'category': 'Cruiser Bikes', 'supplier': 'Premium Bike Suppliers', 'price': 35000, 'cost_price': 25000, 'quantity': 12, 'min_stock': 5, 'brand': 'Premium', 'status': 'available'},
            {'name': 'E-Power Electric Bike', 'category': 'Electric Bikes', 'supplier': 'Yamaha Motors', 'price': 120000, 'cost_price': 90000, 'quantity': 6, 'min_stock': 3, 'brand': 'Yamaha', 'status': 'available'},
            {'name': 'City Commuter E-Bike', 'category': 'Electric Bikes', 'supplier': 'Atlas Honda', 'price': 95000, 'cost_price': 72000, 'quantity': 4, 'min_stock': 3, 'brand': 'Atlas', 'status': 'available'},
            {'name': 'Hybrid X Adventure Bike', 'category': 'Hybrid Bikes', 'supplier': 'Premium Bike Suppliers', 'price': 52000, 'cost_price': 38000, 'quantity': 12, 'min_stock': 5, 'brand': 'Premium', 'status': 'available'},
            {'name': 'Fold-n-Go Compact Folding Bike', 'category': 'Folding Bikes', 'supplier': 'United Spare Parts', 'price': 30000, 'cost_price': 22000, 'quantity': 15, 'min_stock': 5, 'brand': 'United', 'status': 'available'},
            {'name': 'Junior Explorer Kids Bike', 'category': 'Kids Bikes', 'supplier': 'Atlas Honda', 'price': 15000, 'cost_price': 10000, 'quantity': 25, 'min_stock': 10, 'brand': 'Atlas', 'status': 'available'},
            {'name': 'Road King Bicycle', 'category': 'Road Bikes', 'supplier': 'Premium Bike Suppliers', 'price': 28000, 'cost_price': 20000, 'quantity': 20, 'min_stock': 10, 'brand': 'Premium', 'status': 'available'},
            {'name': 'Sohrab Cycle', 'category': 'Road Bikes', 'supplier': 'Atlas Honda', 'price': 12000, 'cost_price': 8500, 'quantity': 30, 'min_stock': 15, 'brand': 'Atlas', 'status': 'available'},
        ]
        products = []
        for data in products_data:
            product = Product.objects.create(
                name=data['name'],
                category=categories[data['category']],
                supplier=suppliers[data['supplier']],
                price=data['price'],
                cost_price=data['cost_price'],
                quantity=data['quantity'],
                min_stock_level=data['min_stock'],
                brand=data['brand'],
                status=data['status'],
            )
            products.append(product)
        self.stdout.write(f'  Created {len(products_data)} products')

        # === SALE ORDERS ===
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        payment_statuses = ['pending', 'paid', 'paid', 'paid', 'partial']

        customers = [
            ('Ahmad Raza', 'ahmad@email.com', '0300-1111111'),
            ('Bilal Khan', 'bilal@email.com', '0300-2222222'),
            ('Farhan Ali', 'farhan@email.com', '0300-3333333'),
            ('Sadia Malik', 'sadia@email.com', '0300-4444444'),
            ('Usman Ghani', 'usman@email.com', '0300-5555555'),
            ('Zainab Bibi', 'zainab@email.com', '0300-6666666'),
            ('Tariq Mehmood', 'tariq@email.com', '0300-7777777'),
            ('Nadia Hussain', 'nadia@email.com', '0300-8888888'),
            ('Kamran Abbas', 'kamran@email.com', '0300-9999999'),
            ('Sana Ali', 'sana@email.com', '0311-0000000'),
        ]

        orders = []
        for i in range(30):
            customer = random.choice(customers)
            status = random.choices(statuses, weights=[3, 3, 2, 3, 1])[0]
            payment = random.choices(payment_statuses, weights=[2, 4, 1, 1, 1])[0]
            hours_ago = random.randint(0, 720)
            order_date = now - timedelta(hours=hours_ago)

            order = SaleOrder.objects.create(
                customer_name=customer[0],
                customer_email=customer[1],
                customer_phone=customer[2],
                order_date=order_date,
                status=status,
                payment_status=payment,
                created_by=random.choice([users['sale_manager'], users['worker1'], users['worker2'], users['worker3']]),
            )

            subtotal = 0
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            for prod in selected_products:
                qty = random.randint(1, 3)
                unit_price = float(prod.price)
                item_subtotal = qty * unit_price
                subtotal += item_subtotal
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=item_subtotal,
                )

            tax = round(subtotal * 0.13, 2)
            total = subtotal + tax
            order.subtotal = subtotal
            order.tax = tax
            order.total_amount = total
            order.save(update_fields=['subtotal', 'tax', 'total_amount'])
            orders.append(order)

        self.stdout.write(f'  Created {len(orders)} sale orders with items')

        # === PURCHASE ORDERS ===
        po_statuses = ['pending', 'accepted', 'shipped', 'delivered', 'cancelled']
        for i in range(10):
            product = random.choice(products)
            qty = random.randint(5, 20)
            unit_price = float(product.cost_price) * random.uniform(0.8, 0.95)
            PurchaseOrder.objects.create(
                supplier=product.supplier,
                product=product,
                quantity=qty,
                unit_price=round(unit_price, 2),
                status=random.choice(po_statuses),
                requested_by=random.choice([users['admin'], users['sale_manager']]),
                order_date=now - timedelta(days=random.randint(1, 30)),
                delivery_date=now + timedelta(days=random.randint(1, 15)),
            )
        self.stdout.write('  Created 10 purchase orders')

        # === TASKS ===
        task_types = ['assembly', 'servicing', 'delivery', 'display', 'stock_check', 'cleaning', 'repair']
        task_titles = [
            'Assemble new Mountain King Pro units',
            'Service customer road bikes',
            'Prepare delivery for order',
            'Update display stock',
            'Monthly stock check',
            'Clean showroom floor',
            'Repair damaged BMX bikes',
            'Install new shelves in warehouse',
            'Organize spare parts inventory',
            'Check and update price tags',
        ]
        workers = [users['worker1'], users['worker2'], users['worker3']]
        for i in range(15):
            assigned = random.choice(workers)
            status = random.choices(['pending', 'in_progress', 'completed'], weights=[3, 2, 5])[0]
            created_days = random.randint(0, 14)
            task = Task.objects.create(
                title=random.choice(task_titles),
                description=f'Task assigned to {assigned.username} for completion.',
                task_type=random.choice(task_types),
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                status=status,
                assigned_to=assigned,
                assigned_by=users['admin'],
                created_at=now - timedelta(days=created_days),
                due_date=now + timedelta(days=random.randint(1, 10)),
            )
            if status == 'completed':
                task.completed_at = now - timedelta(hours=random.randint(1, 48))
                task.save(update_fields=['completed_at'])
        self.stdout.write('  Created 15 tasks')

        # === ISSUES ===
        issue_types = ['damaged', 'missing', 'defective', 'stock_error', 'other']
        severities = ['low', 'medium', 'high', 'critical']
        for i in range(8):
            Issue.objects.create(
                product=random.choice(products),
                reported_by=random.choice(workers),
                assigned_to=random.choice(workers),
                issue_type=random.choice(issue_types),
                severity=random.choice(severities),
                status=random.choice(['pending', 'in_progress', 'resolved']),
                description=f'Issue reported during routine inspection.',
                resolution='Resolved after inspection' if random.random() > 0.5 else '',
                created_at=now - timedelta(days=random.randint(0, 10)),
            )
        self.stdout.write('  Created 8 issues')

        # === ACTIVITY LOGS ===
        actions = ['login', 'logout', 'create_order', 'update_product', 'assign_task', 'resolve_issue', 'update_settings']
        all_users = list(users.values())
        for i in range(50):
            UserActivityLog.objects.create(
                user=random.choice(all_users),
                action=random.choice(actions),
                details=f'Performed {random.choice(actions)} action',
                timestamp=now - timedelta(hours=random.randint(0, 168)),
            )
        self.stdout.write('  Created 50 activity logs')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Products: {Product.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Suppliers: {Supplier.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Sale Orders: {SaleOrder.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Purchase Orders: {PurchaseOrder.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Tasks: {Task.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Issues: {Issue.objects.count()}'))
