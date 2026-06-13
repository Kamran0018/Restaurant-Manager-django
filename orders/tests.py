from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from menu.models import Category, MenuItem
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment


class OrdersViewsTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create category and menu item
        self.category = Category.objects.create(name='Desserts')
        self.menu_item = MenuItem.objects.create(
            name='Chocolate Cake',
            price=250.00,
            category=self.category,
            availability_status=True
        )
        
        # Create cart and cart item for user
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=2
        )

    def test_checkout_login_required(self):
        """Verify checkout view redirects anonymous users to login."""
        response = self.client.get(reverse('orders:checkout'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('orders:checkout')}")

    def test_checkout_view_with_items(self):
        """Verify checkout page renders successfully for logged-in user with items in cart."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')
        self.assertContains(response, 'Chocolate Cake')
        self.assertContains(response, 'Rs. 250')

    def test_checkout_view_empty_cart(self):
        """Verify checkout view redirects to menu list if cart is empty."""
        self.client.login(username='testuser', password='testpassword123')
        self.cart_item.delete()  # empty the cart
        response = self.client.get(reverse('orders:checkout'))
        self.assertRedirects(response, reverse('menu:list'))

    def test_place_order_cash_on_delivery(self):
        """Verify placing an order with cash on delivery creates order, payment, clears cart and redirects to details."""
        self.client.login(username='testuser', password='testpassword123')
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '9876543210',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'zip_code': '123456',
            'payment_method': 'cash',
            'special_instructions': 'No onions'
        }
        
        response = self.client.post(reverse('orders:checkout'), form_data)
        
        # Order should be created
        order = Order.objects.filter(customer=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(order.order_status, Order.OrderStatus.ACCEPTED)
        
        # OrderItem should be created
        order_item = OrderItem.objects.filter(order=order).first()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.menu_item, self.menu_item)
        self.assertEqual(order_item.quantity, 2)
        
        # Payment should be created as completed
        payment = Payment.objects.filter(order=order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_status, Payment.PaymentStatus.COMPLETED)
        self.assertEqual(payment.payment_method, 'cash')
        
        # Cart should be cleared
        self.assertEqual(self.cart.items.count(), 0)
        
        # Should redirect to order detail
        self.assertRedirects(response, reverse('orders:detail', kwargs={'order_id': order.pk}))

    def test_place_order_online_payment(self):
        """Verify placing an order with online payment redirects to payment processing and keeps cart items."""
        self.client.login(username='testuser', password='testpassword123')
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '9876543210',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'zip_code': '123456',
            'payment_method': 'card',
            'special_instructions': ''
        }
        
        response = self.client.post(reverse('orders:checkout'), form_data)
        
        # Order should be created but pending payment
        order = Order.objects.filter(customer=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
        self.assertEqual(order.order_status, Order.OrderStatus.PENDING)
        
        # Payment should be pending
        payment = Payment.objects.filter(order=order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_status, Payment.PaymentStatus.PENDING)
        
        # Cart should NOT be cleared yet
        self.assertEqual(self.cart.items.count(), 1)
        
        # Should redirect to payment page
        self.assertRedirects(response, reverse('payments:process', kwargs={'order_id': order.pk}))
