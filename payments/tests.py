from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from menu.models import Category, MenuItem
from cart.models import Cart, CartItem
from orders.models import Order
from payments.models import Payment


class PaymentsTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='payuser',
            password='paypassword123',
            email='pay@example.com'
        )
        
        # Create category and menu item
        self.category = Category.objects.create(name='Drinks')
        self.menu_item = MenuItem.objects.create(
            name='Mango Lassi',
            price=120.00,
            category=self.category,
            availability_status=True
        )
        
        # Create cart and cart item
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            menu_item=self.menu_item,
            quantity=1
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=self.user,
            total_amount=126.00, # Subtotal + tax
            delivery_address="123 Road",
            order_status=Order.OrderStatus.PENDING,
            payment_status=Order.PaymentStatus.PENDING
        )
        
        # Create payment record
        self.payment = Payment.objects.create(
            order=self.order,
            amount=126.00,
            payment_method='card',
            payment_status=Payment.PaymentStatus.PENDING
        )

    def test_payment_process_login_required(self):
        """Verify anonymous users cannot access payment views."""
        response = self.client.get(reverse('payments:process', kwargs={'order_id': self.order.pk}))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('payments:process', kwargs={'order_id': self.order.pk})}")

    def test_payment_process_success_simulation(self):
        """Verify successful payment simulation updates order, payment, and clears user's cart."""
        self.client.login(username='payuser', password='paypassword123')
        
        # Confirm cart has 1 item before payment completes
        self.assertEqual(self.cart.items.count(), 1)
        
        response = self.client.post(
            reverse('payments:process', kwargs={'order_id': self.order.pk}),
            {'action': 'success'}
        )
        
        # Check payment updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.payment_status, Payment.PaymentStatus.COMPLETED)
        
        # Check order updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(self.order.order_status, Order.OrderStatus.ACCEPTED)
        
        # Cart should be cleared
        self.assertEqual(self.cart.items.count(), 0)
        
        # Should redirect to success page
        self.assertRedirects(response, reverse('payments:success', kwargs={'order_id': self.order.pk}))

    def test_payment_process_failure_simulation(self):
        """Verify failed payment simulation updates order/payment status and keeps cart intact."""
        self.client.login(username='payuser', password='paypassword123')
        
        response = self.client.post(
            reverse('payments:process', kwargs={'order_id': self.order.pk}),
            {'action': 'failure'}
        )
        
        # Check payment updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.payment_status, Payment.PaymentStatus.FAILED)
        
        # Check order updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.FAILED)
        
        # Cart should NOT be cleared
        self.assertEqual(self.cart.items.count(), 1)
        
        # Should redirect to failure page
        self.assertRedirects(response, reverse('payments:failure', kwargs={'order_id': self.order.pk}))
