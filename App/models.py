# models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Bootstrap Icons class, e.g., 'bi-cup-hot'")

    def __str__(self):
        return self.name

# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    roast_level = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('dark', 'Dark'),
    ], blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class logo(models.Model):
    image=models.ImageField(upload_to="logo/")
    
# models.py
class Testimonial(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(default=5)  # 1 to 5
    quote = models.TextField()
    image = models.ImageField(upload_to='Test/')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} – {self.rating}★"
    


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    content = models.TextField(blank=True)  # full content if needed
    image = models.ImageField(upload_to='blog/')
    published_date = models.DateField()
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


class carousel(models.Model):
    image=models.ImageField(upload_to="carousel/")
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_url = models.CharField(max_length=200, default="#")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True)  # for anonymous users
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} - {'User' if self.user else 'Guest'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.product.price * Decimal(self.quantity)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            self.order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user or 'Anonymous'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of purchase

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_number}"

class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="United States")
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.full_name} - {self.address}, {self.city}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('applepay', 'Apple Pay'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # pending, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} payment for Order #{self.order.order_number}"


