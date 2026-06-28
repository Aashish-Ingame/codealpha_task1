import pytest
from django.core.exceptions import ValidationError
from products.models import Product

@pytest.mark.django_db
class TestProductModel:
    """Tests product creation, constraints, validation, and representations."""

    def test_product_saves_correctly_with_valid_fields(self):
        product = Product(
            name="Mechanical Keyboard",
            description="RGB mechanical gaming keyboard.",
            category="electronics",
            price=89.50,
            stock=50,
            rating=4.5
        )
        product.save()
        
        # Verify database save and slug auto-generation
        saved_product = Product.objects.get(id=product.id)
        assert saved_product.name == "Mechanical Keyboard"
        assert saved_product.description == "RGB mechanical gaming keyboard."
        assert saved_product.category == "electronics"
        assert float(saved_product.price) == 89.50
        assert saved_product.stock == 50
        assert saved_product.rating == 4.5
        assert saved_product.slug == "mechanical-keyboard"
        assert saved_product.is_active is True

    def test_price_field_rejects_negative_values(self):
        product = Product(
            name="Negative Price Item",
            description="Invalid item",
            category="clothing",
            price=-10.00,
            stock=10
        )
        # full_clean() should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            product.full_clean()
        assert 'price' in exc_info.value.message_dict

    def test_stock_field_rejects_negative_values(self):
        product = Product(
            name="Negative Stock Item",
            description="Invalid item",
            category="clothing",
            price=15.00,
            stock=-5
        )
        with pytest.raises(ValidationError) as exc_info:
            product.full_clean()
        assert 'stock' in exc_info.value.message_dict

    def test_str_returns_product_name(self):
        product = Product(name="Vintage T-Shirt")
        assert str(product) == "Vintage T-Shirt"

    def test_default_rating_is_zero_point_zero(self):
        product = Product(
            name="No Rating Item",
            description="Item description",
            category="books",
            price=12.99,
            stock=10
        )
        product.save()
        assert product.rating == 0.0

    def test_category_choices_only_accept_defined_values(self):
        product = Product(
            name="Invalid Category Item",
            description="Item description",
            category="invalid_category",  # Not in CATEGORY_CHOICES
            price=12.99,
            stock=10
        )
        with pytest.raises(ValidationError) as exc_info:
            product.full_clean()
        assert 'category' in exc_info.value.message_dict
