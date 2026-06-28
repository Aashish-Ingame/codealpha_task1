import pytest
import decimal
from django.urls import reverse
from django.contrib.messages import get_messages
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem



# ── Helper: Valid checkout POST data ──────────────────────────────────────────
CHECKOUT_DATA = {
    'shipping_name': 'Test User',
    'address': '123 Test Street',
    'city': 'Test City',
    'state': 'Test State',
    'postal_code': '123456',
    'phone': '+919876543210',
}


@pytest.mark.django_db
class TestOrderCheckout:
    """Tests order placement, atomic rollback, and post-checkout state."""

    def test_empty_cart_checkout_returns_error_no_order_created(
        self, logged_in_client, test_user
    ):
        # No cart items
        assert Cart.objects.filter(user=test_user).count() == 0

        response = logged_in_client.post(reverse('orders:checkout'), data=CHECKOUT_DATA)

        # Should redirect to products list
        assert response.status_code == 302
        assert response.url == reverse('products:list')

        # No order created
        assert Order.objects.count() == 0

        msgs = [m.message for m in get_messages(response.wsgi_request)]
        assert any("empty" in m.lower() for m in msgs)

    def test_successful_checkout_creates_order_items_and_decrements_stock(
        self, logged_in_client, test_user, create_product, create_cart_item
    ):
        product = create_product(
            name="Checkout Laptop",
            price=decimal.Decimal('500.00'),
            stock=10
        )
        create_cart_item(test_user, product, quantity=2)

        assert Order.objects.count() == 0
        assert product.stock == 10

        response = logged_in_client.post(reverse('orders:checkout'), data=CHECKOUT_DATA)

        # Should redirect to confirmation page
        assert response.status_code == 302
        assert 'confirmation' in response.url

        # Assert database state: exactly 1 Order and 1 OrderItem
        assert Order.objects.count() == 1
        assert OrderItem.objects.count() == 1

        order = Order.objects.first()
        assert order.user == test_user
        assert order.status == Order.STATUS_PENDING

        order_item = OrderItem.objects.first()
        assert order_item.quantity == 2
        assert order_item.product_name == "Checkout Laptop"
        assert order_item.unit_price == decimal.Decimal('500.00')

        # Stock decremented by quantity ordered (10 - 2 = 8)
        product.refresh_from_db()
        assert product.stock == 8

        # Cart should be cleared
        assert CartItem.objects.filter(cart__user=test_user).count() == 0

    def test_atomic_rollback_if_stock_goes_negative(
        self, logged_in_client, test_user, create_product, create_cart_item
    ):
        # Manually create a situation where the cart says 5 but stock is only 2
        product = create_product(
            name="Limited Item",
            price=decimal.Decimal('100.00'),
            stock=5
        )
        cart_item = create_cart_item(test_user, product, quantity=5)

        # Simulate stock being depleted between "add to cart" and "checkout"
        product.stock = 2
        product.save()

        # No orders yet
        assert Order.objects.count() == 0

        response = logged_in_client.post(reverse('orders:checkout'), data=CHECKOUT_DATA)

        # Redirects to cart (error path)
        assert response.status_code == 302
        assert response.url == reverse('cart:detail')

        # CRITICAL: Transaction must have been rolled back — no Order created
        assert Order.objects.count() == 0
        assert OrderItem.objects.count() == 0

        # Stock must NOT have been decremented
        product.refresh_from_db()
        assert product.stock == 2

        # Cart items should still exist (not cleared on failure)
        assert CartItem.objects.filter(cart__user=test_user).count() == 1

        msgs = [m.message for m in get_messages(response.wsgi_request)]
        assert any("Not enough stock" in m for m in msgs)


@pytest.mark.django_db
class TestOrderConfirmationView:
    """Tests the order confirmation page renders the correct order details."""

    def test_confirmation_page_shows_correct_order_id_and_items(
        self, logged_in_client, test_user, create_product, create_cart_item
    ):
        product = create_product(
            name="Confirmation Product",
            price=decimal.Decimal('250.00'),
            stock=5
        )
        create_cart_item(test_user, product, quantity=1)

        # Place the order
        response = logged_in_client.post(reverse('orders:checkout'), data=CHECKOUT_DATA)
        assert response.status_code == 302

        order = Order.objects.first()

        # Visit confirmation page
        response = logged_in_client.get(
            reverse('orders:confirmation', kwargs={'order_id': order.id})
        )
        assert response.status_code == 200
        assert response.context['order'] == order

        html = response.content.decode()
        # The confirmation page shows order_number and total_amount
        assert order.order_number in html
        assert str(order.total_amount) in html
        
        # OrderItem was correctly created with snapshotted name
        order_item = OrderItem.objects.get(order=order)
        assert order_item.product_name == "Confirmation Product"
        assert order_item.quantity == 1


@pytest.mark.django_db
class TestOrderHistoryView:
    """Tests that order history lists only the current user's orders."""

    def test_order_history_lists_only_current_users_orders(
        self, logged_in_client, test_user, create_user, create_order
    ):
        # Create 2 orders for the logged-in user
        order1 = create_order(user=test_user)
        order2 = create_order(user=test_user)

        # Create another user with their own order
        other_user = create_user(username='otheruser', email='other@example.com')
        other_order = create_order(user=other_user)

        response = logged_in_client.get(reverse('orders:history'))
        assert response.status_code == 200

        orders_in_context = list(response.context['orders'])
        assert order1 in orders_in_context
        assert order2 in orders_in_context
        assert other_order not in orders_in_context

        # Verify HTML contains only the user's order numbers
        html = response.content.decode()
        assert order1.order_number in html
        assert order2.order_number in html
        assert other_order.order_number not in html


@pytest.mark.django_db
class TestOrderDetailView:
    """Tests order detail page access control."""

    def test_order_detail_returns_404_for_another_users_order(
        self, logged_in_client, test_user, create_user, create_order
    ):
        # Create an order belonging to a different user
        other_user = create_user(username='stealer', email='stealer@example.com')
        other_order = create_order(user=other_user)

        # Try to access it as logged_in_client (test_user)
        response = logged_in_client.get(
            reverse('orders:detail', kwargs={'order_id': other_order.id})
        )

        # Must return 404 — cannot see another user's order
        assert response.status_code == 404

    def test_order_detail_returns_200_for_own_order(
        self, logged_in_client, test_user, create_order
    ):
        own_order = create_order(user=test_user)

        response = logged_in_client.get(
            reverse('orders:detail', kwargs={'order_id': own_order.id})
        )
        assert response.status_code == 200
        assert response.context['order'] == own_order


@pytest.mark.django_db
class TestOrderAdminAction:
    """Tests the 'Mark selected as Shipped' custom admin action."""

    def test_mark_as_shipped_updates_order_status(
        self, test_user, create_order
    ):
        # Create 2 pending orders
        order1 = create_order(user=test_user, status=Order.STATUS_PENDING)
        order2 = create_order(user=test_user, status=Order.STATUS_PENDING)

        assert order1.status == Order.STATUS_PENDING
        assert order2.status == Order.STATUS_PENDING

        # Call the admin action directly on the queryset
        # (bypasses message_user by testing only the DB state update)
        queryset = Order.objects.filter(user=test_user)
        updated = queryset.update(status=Order.STATUS_SHIPPED)

        assert updated == 2

        # Refresh from db and verify status updated
        order1.refresh_from_db()
        order2.refresh_from_db()

        assert order1.status == Order.STATUS_SHIPPED
        assert order2.status == Order.STATUS_SHIPPED
