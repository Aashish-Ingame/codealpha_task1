import pytest
import decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()

@pytest.mark.django_db
class TestRegistrationView:
    """Tests registration validation, hashing, duplicates, and redirect flow."""

    def test_valid_registration(self, client, user_data):
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 302
        assert response.url == reverse('accounts:login')
        
        # Verify user was created in the database
        user = User.objects.get(username=user_data['username'])
        assert user.email == user_data['email']
        assert user.full_name == user_data['full_name']
        assert user.phone == user_data['phone']
        assert user.address == user_data['address']
        
        # Verify password is encrypted and hashed
        assert user.check_password(user_data['password1'])
        assert user.password != user_data['password1']

    def test_duplicate_username_returns_form_error(self, client, create_user, user_data):
        # Create an existing user with the same username
        create_user(username=user_data['username'])
        
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 200
        
        form = response.context['form']
        assert 'username' in form.errors
        assert any("already exists" in err for err in form.errors['username'])

    def test_duplicate_email_returns_form_error(self, client, create_user, user_data):
        # Create an existing user with the same email
        create_user(email=user_data['email'], username='other_user')
        
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 200
        
        form = response.context['form']
        assert 'email' in form.errors
        assert any("already exists" in err for err in form.errors['email'])

    def test_password_shorter_than_8_chars_is_rejected(self, client, user_data):
        user_data['password1'] = 'short'
        user_data['password2'] = 'short'
        
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 200
        
        form = response.context['form']
        password_error_field = 'password1' if 'password1' in form.errors else 'password2'
        assert password_error_field in form.errors
        assert any("at least 8 characters" in err.lower() or "too short" in err.lower() for err in form.errors[password_error_field])

    def test_mismatched_confirm_password_is_rejected(self, client, user_data):
        user_data['password2'] = 'different_password'
        
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 200
        
        form = response.context['form']
        assert 'password2' in form.errors or '__all__' in form.errors

    def test_missing_required_fields_show_errors(self, client, user_data):
        user_data['full_name'] = ''
        user_data['phone'] = ''
        user_data['address'] = ''
        
        response = client.post(reverse('accounts:register'), data=user_data)
        assert response.status_code == 200
        
        form = response.context['form']
        assert 'full_name' in form.errors
        assert 'phone' in form.errors
        assert 'address' in form.errors


@pytest.mark.django_db
class TestLoginView:
    """Tests successful/failed login flows, session setting, and error reporting."""

    def test_valid_credentials_log_user_in_and_redirect_to_home(self, client, test_user):
        data = {
            'username': test_user.username,
            'password': 'password123'
        }
        response = client.post(reverse('accounts:login'), data=data)
        
        assert response.status_code == 302
        assert response.url == reverse('home')
        assert '_auth_user_id' in client.session
        assert int(client.session['_auth_user_id']) == test_user.id

    def test_wrong_password_shows_invalid_credentials_error(self, client, test_user):
        data = {
            'username': test_user.username,
            'password': 'wrong_password'
        }
        response = client.post(reverse('accounts:login'), data=data)
        
        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Invalid credentials." in messages
        assert '_auth_user_id' not in client.session

    def test_non_existent_username_shows_error(self, client):
        data = {
            'username': 'does_not_exist',
            'password': 'password123'
        }
        response = client.post(reverse('accounts:login'), data=data)
        
        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Invalid credentials." in messages
        assert '_auth_user_id' not in client.session

    def test_empty_fields_show_validation_errors(self, client):
        data = {
            'username': '',
            'password': ''
        }
        response = client.post(reverse('accounts:login'), data=data)
        
        assert response.status_code == 200
        form = response.context['form']
        assert 'username' in form.errors
        assert 'password' in form.errors

    def test_login_sets_session_correctly(self, client, test_user):
        data = {
            'username': test_user.username,
            'password': 'password123'
        }
        client.post(reverse('accounts:login'), data=data)
        
        # Assert user ID is stored in the session and matches
        assert client.session.get('_auth_user_id') is not None
        assert int(client.session.get('_auth_user_id')) == test_user.id


@pytest.mark.django_db
class TestLogoutView:
    """Tests that logging out destroys sessions and rejects non-POST requests."""

    def test_post_logout_destroys_session_and_redirects_to_home(self, logged_in_client):
        # Verify user is logged in
        assert '_auth_user_id' in logged_in_client.session
        
        response = logged_in_client.post(reverse('accounts:logout'))
        
        assert response.status_code == 302
        assert response.url == reverse('home')
        assert '_auth_user_id' not in logged_in_client.session

    def test_get_logout_is_rejected_405(self, logged_in_client):
        # Verify user is logged in
        assert '_auth_user_id' in logged_in_client.session
        
        response = logged_in_client.get(reverse('accounts:logout'))
        
        assert response.status_code == 405
        # The user session must not be destroyed on a rejected GET request
        assert '_auth_user_id' in logged_in_client.session


@pytest.mark.django_db
class TestProfileView:
    """Tests access controls, user data presentation, and order history containment."""

    def test_unauthenticated_access_redirects_to_login(self, client):
        response = client.get(reverse('accounts:profile'))
        assert response.status_code == 302
        
        expected_redirect = f"{reverse('accounts:login')}?next={reverse('accounts:profile')}"
        assert response.url == expected_redirect

    def test_profile_page_shows_correct_user_info(self, logged_in_client, test_user):
        response = logged_in_client.get(reverse('accounts:profile'))
        
        assert response.status_code == 200
        content = response.content.decode()
        assert test_user.username in content
        assert test_user.email in content
        assert test_user.full_name in content
        assert test_user.phone in content
        assert test_user.address in content

    def test_order_history_table_shows_all_orders_for_that_user_only(
        self, logged_in_client, test_user, create_user, create_order
    ):
        # Create orders for the logged-in user (user 1)
        order1 = create_order(user=test_user, total_amount=decimal.Decimal('1500.00'), status='pending')
        order2 = create_order(user=test_user, total_amount=decimal.Decimal('250.75'), status='shipped')
        
        # Create a second user and their order
        user2 = create_user(username='other_user', email='other_user@example.com')
        order3 = create_order(user=user2, total_amount=decimal.Decimal('899.99'), status='delivered')
        
        response = logged_in_client.get(reverse('accounts:profile'))
        assert response.status_code == 200
        
        # Check context variable "orders"
        orders_in_context = response.context['orders']
        assert order1 in orders_in_context
        assert order2 in orders_in_context
        assert order3 not in orders_in_context
        
        # Check that the order list shows only the user's orders in the HTML
        html_content = response.content.decode()
        assert order1.order_number in html_content
        assert order2.order_number in html_content
        assert order3.order_number not in html_content
        
        # Verify status CSS color classes are present in the table
        assert "status-pending" in html_content
        assert "status-shipped" in html_content
        assert "status-delivered" not in html_content
