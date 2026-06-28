import pytest
from django.urls import reverse
from products.models import Product

@pytest.mark.django_db
class TestProductListView:
    """Tests product list page, search functionality, filters, sorting, and pagination."""

    def test_get_products_list_returns_200_and_context(self, client, seeded_products):
        # GET /shop/ (reversable via products:list)
        response = client.get(reverse('products:list'))
        assert response.status_code == 200
        
        # Verify page_obj is in context and has the correct number of products
        assert 'page_obj' in response.context
        assert len(response.context['page_obj']) == 8  # Page limit is 8
        assert 'categories' in response.context

    def test_search_by_query_returns_matching_products(self, client, seeded_products):
        # Search for "laptop" (should return only Laptop)
        response = client.get(reverse('products:list'), {'q': 'laptop'})
        assert response.status_code == 200
        
        products = response.context['page_obj'].object_list
        assert len(products) == 1
        assert products[0].name == "Laptop"

    def test_filter_by_category_returns_only_matching_category(self, client, seeded_products):
        # Filter by electronics
        response = client.get(reverse('products:list'), {'category': 'electronics'})
        assert response.status_code == 200
        
        products = response.context['page_obj'].object_list
        assert len(products) == 4  # 4 electronics items in fixture
        for p in products:
            assert p.category == 'electronics'

    def test_filter_by_price_range_filters_correctly(self, client, seeded_products):
        # Filter range 100 to 500 (inclusive)
        # Seeded products in range:
        # - Wireless Headphones (149.99)
        # - Out of Stock Tablet (299.99)
        # - Leather Jacket (199.99)
        response = client.get(reverse('products:list'), {'min_price': '100', 'max_price': '500'})
        assert response.status_code == 200
        
        products = response.context['page_obj'].object_list
        assert len(products) == 3
        for p in products:
            assert float(p.price) >= 100.0
            assert float(p.price) <= 500.0

    def test_sorting_by_price_asc_returns_lowest_first(self, client, seeded_products):
        # Sort price ascending
        response = client.get(reverse('products:list'), {'sort': 'price_asc'})
        assert response.status_code == 200
        
        # We need to look across all page objects or verify sorting
        # Since it's page 1, verify sorted on page 1
        products = list(response.context['page_obj'].object_list)
        prices = [float(p.price) for p in products]
        assert prices == sorted(prices)

    def test_pagination_limits_pages_correctly(self, client, seeded_products):
        # Page 1
        response_page1 = client.get(reverse('products:list'))
        assert response_page1.status_code == 200
        assert len(response_page1.context['page_obj']) == 8
        
        # Page 2
        response_page2 = client.get(reverse('products:list'), {'page': '2'})
        assert response_page2.status_code == 200
        assert len(response_page2.context['page_obj']) == 4  # Remaining 4 out of 12

    def test_empty_search_returns_empty_list_safely(self, client, seeded_products):
        # Search query with zero matches
        response = client.get(reverse('products:list'), {'q': 'xyzabc'})
        assert response.status_code == 200
        
        assert len(response.context['page_obj']) == 0


@pytest.mark.django_db
class TestProductDetailView:
    """Tests the product detail page for valid, invalid, and out-of-stock items."""

    def test_get_valid_product_detail_returns_200_and_context(self, client, seeded_products):
        # Fetch Laptop details
        laptop = Product.objects.get(name="Laptop")
        response = client.get(reverse('products:detail', kwargs={'slug': laptop.slug}))
        
        assert response.status_code == 200
        assert 'product' in response.context
        assert response.context['product'] == laptop
        assert laptop.name in response.content.decode()

    def test_invalid_product_detail_returns_404(self, client, seeded_products):
        # Non-existent slug
        response = client.get(reverse('products:detail', kwargs={'slug': 'non-existent-slug'}))
        assert response.status_code == 404

    def test_out_of_stock_product_shows_disabled_add_to_cart(self, client, seeded_products):
        # Out of Stock Tablet
        tablet = Product.objects.get(name="Out of Stock Tablet")
        response = client.get(reverse('products:detail', kwargs={'slug': tablet.slug}))
        
        assert response.status_code == 200
        html = response.content.decode()
        
        # Assert disabled indicator is in template output
        assert 'disabled' in html
        assert 'Out of Stock' in html
        # Form action URL to add to cart should not be present
        assert reverse('cart:add', args=[tablet.id]) not in html
