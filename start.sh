#!/usr/bin/env bash
# ==================================
# RENDER DEPLOY SCRIPT FOR DJANGO
# ==================================
set -o errexit  # Exit immediately on error

# ----------------------------
# INSTALL DEPENDENCIES
# ----------------------------
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# ----------------------------
# RUN DATABASE MIGRATIONS
# ----------------------------
echo "🛠 Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# ----------------------------
# COLLECT STATIC FILES
# ----------------------------
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# ----------------------------
# CREATE SUPERUSER IF NOT EXISTS
# ----------------------------
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin123}

echo "🔍 Checking if superuser exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Superuser '{username}' created.")
else:
    print(f"ℹ️ Superuser '{username}' already exists.")
END

# ----------------------------
# CREATE DEFAULT CATEGORIES & SAMPLE PRODUCTS
# ----------------------------
echo "🛒 Creating default categories and sample products..."
python manage.py shell << END
from products.models import Category, Product

# --- DEFAULT CATEGORIES ---
default_categories = [
    {"name": "Tech Accessories", "slug": "tech-accessories"},
    {"name": "Custom T-Shirts", "slug": "custom-tshirts"},
    {"name": "Gadgets", "slug": "gadgets"},
]

for cat_data in default_categories:
    cat, created = Category.objects.get_or_create(
        slug=cat_data["slug"],
        defaults={"name": cat_data["name"], "is_active": True}
    )
    if created:
        print(f"✅ Category '{cat.name}' created.")

# --- SAMPLE PRODUCTS ---
sample_products = [
    {
        "name": "Wireless Mouse",
        "slug": "wireless-mouse",
        "price": 49.99,
        "is_featured": True,
        "is_active": True,
        "category_slug": "tech-accessories"
    },
    {
        "name": "Graphic T-Shirt",
        "slug": "graphic-tshirt",
        "price": 29.99,
        "is_featured": True,
        "is_active": True,
        "category_slug": "custom-tshirts"
    },
]

for p in sample_products:
    cat = Category.objects.get(slug=p["category_slug"])
    prod, created = Product.objects.get_or_create(
        slug=p["slug"],
        defaults={
            "name": p["name"],
            "price": p["price"],
            "is_featured": p["is_featured"],
            "is_active": p["is_active"],
            "category": cat,
        }
    )
    if created:
        print(f"✅ Product '{prod.name}' created.")

END

# ----------------------------
# START GUNICORN
# ----------------------------
echo "🚀 Starting server..."
gunicorn ecommerce.wsgi:application
