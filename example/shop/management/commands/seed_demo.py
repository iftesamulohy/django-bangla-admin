"""Seed the demo project with users, categories, products and orders.

Run::

    python manage.py seed_demo

Idempotent-ish: it clears existing demo rows first so charts/activity always
look alive after a fresh run. Also ensures an admin/admin superuser exists.
"""

import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from shop.models import Category, Order, Product

CATEGORIES = ["Electronics", "Fashion", "Grocery", "Books", "Home & Living"]
PRODUCTS = {
    "Electronics": ["Smartphone", "Headphones", "Laptop", "Smartwatch", "Power Bank"],
    "Fashion": ["T-Shirt", "Sneakers", "Panjabi", "Saree", "Denim Jacket"],
    "Grocery": ["Basmati Rice 5kg", "Mustard Oil 1L", "Tea 500g", "Lentils 1kg"],
    "Books": ["Bangla Novel", "Python Crash Course", "History of Bengal"],
    "Home & Living": ["Table Lamp", "Cushion Set", "Wall Clock", "Cookware Set"],
}
CUSTOMERS = ["Rahim", "Karim", "Ayesha", "Sumaiya", "Tanvir", "Nadia", "Jamil", "Mitu"]


class Command(BaseCommand):
    help = "Seed the demo project with sample shop data."

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(self.style.SUCCESS("Created superuser admin/admin"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        cats = {}
        for name in CATEGORIES:
            cats[name] = Category.objects.create(name=name, slug=name.lower().replace(" & ", "-").replace(" ", "-"))

        products = []
        for cat_name, items in PRODUCTS.items():
            for item in items:
                products.append(Product.objects.create(
                    name=item,
                    category=cats[cat_name],
                    price=Decimal(random.randint(150, 95000)),
                    stock=random.randint(0, 250),
                    is_active=random.random() > 0.1,
                ))

        statuses = [s[0] for s in Order.STATUS]
        now = timezone.now()
        for _ in range(120):
            product = random.choice(products)
            qty = random.randint(1, 5)
            order = Order.objects.create(
                customer_name=random.choice(CUSTOMERS),
                product=product,
                quantity=qty,
                total=product.price * qty,
                status=random.choice(statuses),
            )
            # Backdate across the last 30 days for a believable timeline.
            order.created_at = now - timezone.timedelta(
                days=random.randint(0, 29), hours=random.randint(0, 23)
            )
            order.save(update_fields=["created_at"])

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(cats)} categories, {len(products)} products, "
            f"{Order.objects.count()} orders."
        ))
