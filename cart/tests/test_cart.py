import pytest
import json
import decimal
from django.urls import reverse
from django.contrib.messages import get_messages
from cart.models import Cart, CartItem
from cart.context_processors import cart_count
from django.test import RequestFactory

@pytest.mark.django_db
class TestCartOperations:
    """Tests viewing, adding, updating, removing, and clearing the shopping cart."""

    def test_adding_product_creates_cart_and_cart_item(self, logged_in_client, test_user, create_product):
        product = create_product(name="Unique Keyboard", price=decimal.Decimal('100.00'), stock=5)
        
        # Verify initial database state
        assert Cart.objects.filter(user=test_user).count() == 0
        assert CartItem.objects.count() == 0
        
        response = logged_in_client.post(reverse('cart:add', args=[product.id]), {'quantity': 1})
        assert response.status_code == 302
        assert response.url == reverse('cart:detail')
        
        # Verify Cart and CartItem created
        assert Cart.objects.filter(user=test_user).count() == 1
        assert CartItem.objects.filter(cart__user=test_user, product=product).count() == 1
        
        item = CartItem.objects.get(cart__user=test_user, product=product)
        assert item.quantity == 1

    def test_adding_same_product_again_increments_quantity(self, logged_in_client, test_user, create_product):
        product = create_product(name="Standard Mouse", price=decimal.Decimal('20.00'), stock=10)
        
        # Add once
        logged_in_client.post(reverse('cart:add', args=[product.id]), {'quantity': 2})
        # Add again
        logged_in_client.post(reverse('cart:add', args=[product.id]), {'quantity': 3})
        
        # Verify only one CartItem exists, with incremented quantity of 5
        assert CartItem.objects.filter(cart__user=test_user, product=product).count() == 1
        item = CartItem.objects.get(cart__user=test_user, product=product)
        assert item.quantity == 5

    def test_adding_out_of_stock_product_is_rejected(self, logged_in_client, test_user, create_product):
        # Product with stock = 0
        product = create_product(name="Out of Stock TV", price=decimal.Decimal('500.00'), stock=0)
        
        response = logged_in_client.post(reverse('cart:add', args=[product.id]), {'quantity': 1})
        
        # Should redirect back to product details page
        assert response.status_code == 302
        assert response.url == reverse('products:detail', kwargs={'slug': product.slug})
        
        # Verify no cart item created
        assert CartItem.objects.count() == 0
        
        # Assert error message is present
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert f"Sorry, {product.name} is out of stock." in messages

    def test_updating_quantity_to_zero_removes_item(self, logged_in_client, test_user, create_product, create_cart_item):
        product = create_product(name="Tablet", price=decimal.Decimal('150.00'), stock=5)
        cart_item = create_cart_item(test_user, product, quantity=2)
        
        assert CartItem.objects.filter(id=cart_item.id).count() == 1
        
        # Send AJAX update to 0
        response = logged_in_client.post(
            reverse('cart:update', args=[cart_item.id]),
            data=json.dumps({'quantity': 0}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        assert data['item_removed'] is True
        
        # Verify CartItem is deleted in database
        assert CartItem.objects.filter(id=cart_item.id).count() == 0

    def test_removing_item_decrements_cart_item_count(self, logged_in_client, test_user, create_product, create_cart_item):
        product = create_product(name="Speaker", price=decimal.Decimal('50.00'), stock=10)
        cart_item = create_cart_item(test_user, product, quantity=1)
        
        assert CartItem.objects.filter(cart__user=test_user).count() == 1
        
        response = logged_in_client.post(reverse('cart:remove', args=[cart_item.id]))
        assert response.status_code == 302
        assert response.url == reverse('cart:detail')
        
        # Verify CartItem deleted in DB
        assert CartItem.objects.filter(cart__user=test_user).count() == 0

    def test_clear_cart_deletes_all_cart_items_for_user(self, logged_in_client, test_user, create_product, create_cart_item):
        p1 = create_product(name="Keyboard", price=decimal.Decimal('30.00'), stock=10)
        p2 = create_product(name="Mouse", price=decimal.Decimal('20.00'), stock=10)
        create_cart_item(test_user, p1, quantity=1)
        create_cart_item(test_user, p2, quantity=2)
        
        assert CartItem.objects.filter(cart__user=test_user).count() == 2
        
        response = logged_in_client.post(reverse('cart:clear'))
        assert response.status_code == 302
        assert response.url == reverse('cart:detail')
        
        # Verify cart items are deleted
        assert CartItem.objects.filter(cart__user=test_user).count() == 0

    def test_cart_total_calculates_correctly(self, logged_in_client, test_user, create_product, create_cart_item):
        p1 = create_product(name="Keyboard", price=decimal.Decimal('100.00'), stock=10)
        p2 = create_product(name="Mouse", price=decimal.Decimal('50.00'), stock=10)
        
        # Total: 1*100 + 2*50 = 200
        create_cart_item(test_user, p1, quantity=1)
        create_cart_item(test_user, p2, quantity=2)
        
        response = logged_in_client.get(reverse('cart:detail'))
        assert response.status_code == 200
        
        # subtotal: 200.00
        # tax: 200.00 * 0.18 = 36.00
        # shipping: 50.00
        # grand_total: 286.00
        assert response.context['subtotal'] == decimal.Decimal('200.00')
        assert response.context['tax'] == decimal.Decimal('36.00')
        assert response.context['shipping'] == decimal.Decimal('50.00')
        assert response.context['grand_total'] == decimal.Decimal('286.00')

    def test_unauthenticated_user_is_redirected_to_login(self, client, create_product):
        product = create_product(name="Unauthorized Item", price=decimal.Decimal('100.00'))
        
        urls = [
            reverse('cart:detail'),
            reverse('cart:add', args=[product.id]),
            reverse('cart:update', args=[1]),
            reverse('cart:remove', args=[1]),
            reverse('cart:clear'),
        ]
        
        login_url = reverse('accounts:login')
        for url in urls:
            # We test both GET and POST requests for these URLs
            response = client.post(url) if url != reverse('cart:detail') else client.get(url)
            assert response.status_code == 302
            assert login_url in response.url

    def test_cart_count_context_processor_returns_correct_count(self, test_user, create_product, create_cart_item):
        rf = RequestFactory()
        
        # 1. Anonymous User
        req = rf.get('/')
        class AnonUser:
            is_authenticated = False
        req.user = AnonUser()
        assert cart_count(req) == {'cart_count': 0}
        
        # 2. Authenticated User with no cart items
        req.user = test_user
        assert cart_count(req) == {'cart_count': 0}
        
        # 3. Authenticated User with cart items
        p1 = create_product(name="P1", price=decimal.Decimal('10.00'), stock=10)
        p2 = create_product(name="P2", price=decimal.Decimal('20.00'), stock=10)
        create_cart_item(test_user, p1, quantity=3)
        create_cart_item(test_user, p2, quantity=2)
        
        assert cart_count(req) == {'cart_count': 5}
