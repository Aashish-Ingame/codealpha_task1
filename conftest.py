import pytest
import decimal
import django.test.client
from accounts.models import User
from products.models import Product
from cart.models import Cart, CartItem
from orders.models import Order

# Monkeypatch django.test.client.store_rendered_templates to avoid a Python 3.14 compatibility bug
# with copy(context) on django.template.Context objects.
def patched_store_rendered_templates(store, signal, sender, template, context, **kwargs):
    from django.test.utils import ContextList
    store.setdefault("templates", []).append(template)
    if context is not None:
        if "context" not in store:
            store["context"] = ContextList()
        store["context"].append(context)

django.test.client.store_rendered_templates = patched_store_rendered_templates


@pytest.fixture
def user_data():
    """Returns valid registration form data."""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password1': 'P@ssw0rd_Str0ng_99',
        'password2': 'P@ssw0rd_Str0ng_99',
        'full_name': 'Test User',
        'phone': '+919876543210',
        'address': '123 E-commerce Street, Shop City',
    }


@pytest.fixture
def create_user(db):
    """Fixture to programmatically create a user with a hashed password."""
    def make_user(**kwargs):
        password = kwargs.pop('password', 'password123')
        username = kwargs.pop('username', 'testuser')
        email = kwargs.pop('email', 'testuser@example.com')
        full_name = kwargs.pop('full_name', 'Test User')
        phone = kwargs.pop('phone', '+919876543210')
        address = kwargs.pop('address', '123 E-commerce Street, Shop City')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            full_name=full_name,
            phone=phone,
            address=address,
            **kwargs
        )
        return user
    return make_user


@pytest.fixture
def test_user(db, create_user):
    """Fixture to provide a pre-created test user."""
    return create_user()


@pytest.fixture
def logged_in_client(client, test_user):
    """Fixture to provide a client logged in as test_user."""
    client.login(username=test_user.username, password='password123')
    return client


@pytest.fixture
def create_product(db):
    """Fixture to programmatically create a product with valid fields."""
    def make_product(**kwargs):
        defaults = {
            'name': 'Sample Product',
            'description': 'Product description',
            'category': 'electronics',
            'price': decimal.Decimal('100.00'),
            'stock': 10,
            'rating': 4.0
        }
        defaults.update(kwargs)
        product = Product(**defaults)
        product.save()
        return product
    return make_product


@pytest.fixture
def seeded_products(db, create_product):
    """Creates 12 products across 3 categories (electronics, clothing, books)."""
    products = [
        # Electronics
        create_product(name="Laptop", description="High-performance work laptop.", category="electronics", price=decimal.Decimal('899.99'), stock=15, rating=4.5),
        create_product(name="Smartphone", description="Latest generation smartphone.", category="electronics", price=decimal.Decimal('599.99'), stock=8, rating=4.2),
        create_product(name="Wireless Headphones", description="Noise-cancelling over-ear headphones.", category="electronics", price=decimal.Decimal('149.99'), stock=25, rating=4.0),
        create_product(name="Out of Stock Tablet", description="Sleek tablet with stylus support.", category="electronics", price=decimal.Decimal('299.99'), stock=0, rating=3.8),
        
        # Clothing
        create_product(name="Leather Jacket", description="Classic brown leather jacket.", category="clothing", price=decimal.Decimal('199.99'), stock=5, rating=4.7),
        create_product(name="Denim Jeans", description="Comfortable slim-fit denim jeans.", category="clothing", price=decimal.Decimal('49.99'), stock=30, rating=4.3),
        create_product(name="Graphic T-Shirt", description="100% cotton casual t-shirt.", category="clothing", price=decimal.Decimal('19.99'), stock=100, rating=4.1),
        create_product(name="Running Shoes", description="Lightweight athletic running shoes.", category="clothing", price=decimal.Decimal('89.99'), stock=12, rating=4.4),
        
        # Books
        create_product(name="Python Programming Guide", description="Master python coding in 30 days.", category="books", price=decimal.Decimal('39.99'), stock=20, rating=4.9),
        create_product(name="Sci-Fi Novel", description="An epic adventure across galaxies.", category="books", price=decimal.Decimal('9.99'), stock=50, rating=4.0),
        create_product(name="World History Book", description="A comprehensive guide to world history.", category="books", price=decimal.Decimal('29.99'), stock=10, rating=4.5),
        create_product(name="Vegetarian Cookbook", description="Healthy and delicious vegetarian recipes.", category="books", price=decimal.Decimal('24.99'), stock=18, rating=4.2),
    ]
    return products


@pytest.fixture
def create_cart_item(db):
    """Fixture to programmatically add an item to a user's cart."""
    def make_cart_item(user, product, quantity=1):
        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity = quantity
            item.save()
        return item
    return make_cart_item


@pytest.fixture
def create_order(db):
    """Fixture to programmatically create an order for a user."""
    def make_order(user, **kwargs):
        defaults = {
            'shipping_name': user.full_name or user.username,
            'address': user.address or '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '123456',
            'phone': user.phone or '1234567890',
            'total_amount': decimal.Decimal('1500.00'),
            'status': 'pending',
        }
        defaults.update(kwargs)
        return Order.objects.create(user=user, **defaults)
    return make_order
