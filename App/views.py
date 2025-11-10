from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
from .models import Product, Testimonial, BlogPost, ContactMessage,logo,carousel



def login_view(request):
    context = {
        'logos': logo.objects.all(),
       
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # not used here, but you can handle session timeout

        # Find user by email (Django User has username, so we search by email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

        # Authenticate
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to confirmed page after login
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html',context)


def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        subscribe = request.POST.get('subscribe')  # checkbox value

        # Validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email already registered.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signup.html', {'full_name': full_name, 'email': email})

        # Create user
        username = email.split('@')[0]  # Simple username from email
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name.split()[0] if ' ' in full_name else full_name,
            last_name=' '.join(full_name.split()[1:]) if ' ' in full_name else ''
        )
        user.save()

        # Optional: Subscribe to newsletter (store in profile or session)
        if subscribe:
            # You could store this in a Profile model or session
            pass

        # Log the user in automatically
        login(request, user)
        return redirect('confirmed_page')
    context = {
        'logos': logo.objects.all(),
       
    }

    return render(request, 'signup.html',context)


def confirmed_view(request):
   
    return render(request, 'confirmed.html')

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Testimonial, BlogPost

def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.count()  # assuming related_name='items'
        except Cart.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.items.count()
            except Cart.DoesNotExist:
                count = 0
    return {'cart_item_count': count}

from django.shortcuts import render
from .models import Category, Product, Testimonial, BlogPost, logo

def home(request):
    # Get selected category from URL query param
    selected_category_name = request.GET.get('category')
    
    # Fetch all data
    logos = logo.objects.all()
    carousels=carousel.objects.all()
    categories = Category.objects.all()
    featured_testimonial = Testimonial.objects.filter(is_featured=True).first()
    other_testimonials = Testimonial.objects.exclude(is_featured=True)[:3]
    blog_posts = BlogPost.objects.all()[:3]


    # Filter products based on selected category
    if selected_category_name:
        try:
            selected_category = Category.objects.get(name=selected_category_name)
            featured_products = Product.objects.filter(category=selected_category, is_new=True)[:4]
            best_sellers = Product.objects.filter(
                category=selected_category, is_on_sale=False
            ).exclude(id__in=[p.id for p in featured_products])[:4]
        except Category.DoesNotExist:
            # If invalid category, show nothing
            featured_products = Product.objects.none()
            best_sellers = Product.objects.none()
    else:
        # Show all if no category selected
        featured_products = Product.objects.filter(is_new=True)[:8]
        best_sellers = Product.objects.filter(is_on_sale=False)[:4]

    context = {
        "carousels":carousels,
        'logos': logos,
        'categories': categories,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'featured_testimonial': featured_testimonial,
        'other_testimonials': other_testimonials,
        'blog_posts': blog_posts,
        'selected_category': selected_category_name,  # optional: for highlighting
    }
    return render(request, 'home.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Testimonial, Category

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    reviews = Testimonial.objects.filter(product=product).order_by('-created_at')
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'categories': categories,
        'reviews': reviews,
        'related_products': related_products,
        'logos':logo.objects.all()
    }
    return render(request, 'product_detail.html', context)

def submit_review(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        name = request.POST.get('customer_name')
        rating = request.POST.get('rating')
        quote = request.POST.get('quote')

        Testimonial.objects.create(
            product=product,
            customer_name=name,
            rating=int(rating),
            quote=quote
        )
        messages.success(request, "Thank you for your review!")
        return redirect('product_detail', product_id=product.id)
    return redirect('product_detail', product_id=product_id)

# views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, Category
# views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product, Category

def shop(request):
    # Get filters from URL
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'default')
    page = request.GET.get('page', 1)

    # Start with all products
    products = Product.objects.all()

    # Apply category filter
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    # else: default order (by id or creation)

    # Paginate
    paginator = Paginator(products, 9)  # 9 products per page
    products_page = paginator.get_page(page)

    context = {
        'products': products_page,
        'categories': Category.objects.all(),
        'sort_by': sort_by,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
    }
    return render(request, 'shop.html', context)
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingAddress, Payment
import random
from decimal import Decimal
# views.py
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem

def cart_view(request):
    # Get or create a cart
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    # Now safely get cart items
    cart_items = cart.items.all()  # Assumes related_name='items' in CartItem.cart

    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)  # Ensure total_price returns Decimal
    shipping_estimate = Decimal('5.00')
    tax = round(subtotal * Decimal('0.08'), 2)  # 8% tax
    order_total = subtotal + shipping_estimate + tax

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_estimate': shipping_estimate,
        'tax': tax,
        'order_total': order_total,
        'logos':logo.objects.all()
    }
    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart')

def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('cart')

from decimal import Decimal
def shipping_info_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        session_key = request.session.session_key
        cart = Cart.objects.get(session_key=session_key)

    # Calculate order totals
    subtotal = sum(item.total_price for item in cart.items.all())  # Decimal
    shipping_cost = Decimal('5.00')
    tax = round(subtotal * Decimal('0.08'), 2)  # ✅ Fixed: Decimal tax rate
    total = subtotal + shipping_cost + tax

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            cart=cart,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
        )

        # Save shipping address
        ShippingAddress.objects.create(
            order=order,
            full_name=request.POST['full_name'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip_code'],
            country=request.POST.get('country', 'United States'),
            phone_number=request.POST['phone_number'],
        )

        request.session['current_order_id'] = order.id
        return redirect('payment_info')
    context={
        'logos':logo.objects.all()
    }

    return render(request, 'shipping.html',context)

def payment_info_view(request):
    logos=logo.objects.all()
    current_order_id = request.session.get('current_order_id')
    
    if not current_order_id:
        messages.error(request, "No active order found. Please complete shipping first.")
        return redirect('cart')

    try:
        order = Order.objects.get(id=current_order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found. Please restart checkout.")
        del request.session['current_order_id']  # clean up
        return redirect('cart')

    order = get_object_or_404(Order, id=current_order_id)

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'card')
        transaction_id = f"TXN{random.randint(100000, 999999)}"

        Payment.objects.create(
            order=order,
            method=method,
            card_last_four=request.POST.get('card_last_four', '')[-4:] if method == 'card' else '',
            transaction_id=transaction_id,
            amount=order.total,
            status='completed'
        )

        # Update order status
        order.status = 'paid'
        order.save()

        # Create order items from cart items (if cart still exists)
        if order.cart:
            for cart_item in order.cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

        return redirect('review_order')
    

    return render(request, 'payment.html', {'order': order,'logos':logos})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order

def review_order_view(request):
    order_id = request.session.get('current_order_id')
    
    if not order_id:
        messages.error(request, "No active order found. Please complete checkout from the beginning.")
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Your order could not be found. Please restart checkout.")
        # Clean up invalid session key
        if 'current_order_id' in request.session:
            del request.session['current_order_id']
        return redirect('cart')

    # Optional: Ensure order has shipping address and payment
    context = {
        'order': order,
        'shipping': getattr(order, 'shipping_address', None),
        'payment': getattr(order, 'payment', None),
        'logos':logo.objects.all()

    }
    return render(request, 'review.html', context)
def place_order_view(request):
    logos=logo.objects.all()
    order_id = request.session.get('current_order_id')
    if not order_id:
        messages.error(request, "No order found. Please restart checkout.")
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('cart')

    # ✅ Clear the cart AFTER confirming the order
    if request.user.is_authenticated:
        # Delete user's cart
        Cart.objects.filter(user=request.user).delete()
    else:
        # Delete session-based cart
        session_key = request.session.session_key
        if session_key:
            Cart.objects.filter(session_key=session_key).delete()

    # Optional: Clean up session
    if 'current_order_id' in request.session:
        del request.session['current_order_id']

    return render(request, 'confirmation.html', {'order': order,'logos':logos})

    from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def debug_view(request):
    site = Site.objects.get_current()
    apps = SocialApp.objects.filter(sites=site, provider='google')
    print("Current site:", site)
    print("Google apps found:", apps)
    return HttpResponse("Check console")

# App/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from .models import Order, Product, OrderItem
from datetime import datetime, timedelta

  # Only staff can access
def dashboard(request):
    # Sales data (last 30 days)
    # Sales data (last 7 days)
    today = timezone.now().date()
    chart_labels = []
    chart_data = []
    for i in range(7):
        date = today - timedelta(days=6 - i)
        day_total = Order.objects.filter(
            created_at__date=date
        ).aggregate(total=Sum('total'))['total'] or 0
        chart_labels.append(date.strftime('%a %d'))  # e.g., "Mon 15"
        chart_data.append(float(day_total))

    # Other metrics
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
    total_orders = Order.objects.count()
    avg_order_value = total_revenue / total_orders if total_orders else 0

    # Recent orders & top products
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value, 2),
        'recent_orders': recent_orders,
        'top_products': top_products,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard.html', context)



def admin_order(request):
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Add badge class directly to each order
    for order in orders:
        badge_map = {
            'pending': 'bg-warning text-dark',
            'paid': 'bg-info',
            'shipped': 'bg-primary',
            'delivered': 'bg-success',
        }
        order.badge_class = badge_map.get(order.status, 'bg-secondary')

    return render(request,"admin_order.html",{"orders":orders})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Category
from django.contrib import messages

@staff_member_required
def admin_product(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    return render(request, 'admin_product.html', {'products': products, 'categories': categories})

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        price = request.POST['price']
        category_id = request.POST['category']
        is_new = 'is_new' in request.POST
        is_on_sale = 'is_on_sale' in request.POST
        image = request.FILES['image']

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            image=image,
            category_id=category_id,
            is_new=is_new,
            is_on_sale=is_on_sale
        )
        messages.success(request, "Product added successfully!")
        return redirect('admin_product')
    return render(request, 'admin_product.html')
   

@staff_member_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST.get('description', '')
        product.price = request.POST['price']
        product.category_id = request.POST['category']
        product.is_new = 'is_new' in request.POST
        product.is_on_sale = 'is_on_sale' in request.POST
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        messages.success(request, "Product updated!")
        return redirect('admin_product')
    return render(request,'admin_product.html')

@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('admin_product')

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Order

@staff_member_required
def admin_customer(request):
    customers = User.objects.annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total')
    ).prefetch_related('order_set').order_by('-date_joined')

    # Add recent orders to each customer
    for customer in customers:
        customer.recent_orders = customer.order_set.order_by('-created_at')[:3]

    return render(request, 'admin_customer.html', {'customers': customers})
# App/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Order, Product, User

@staff_member_required
def admin_analytic(request):
    # Date ranges
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)

    # Helper function to get metrics for a date range
    def get_metrics(start_date):
        orders = Order.objects.filter(created_at__gte=start_date)
        revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        order_count = orders.count()
        avg_order = revenue / order_count if order_count else 0
        customer_count = User.objects.filter(date_joined__gte=start_date).count()

        # Revenue trend (daily for week/month, monthly for year)
        if start_date == year_start:
            labels = [(year_start + timedelta(days=30*i)).strftime('%b') for i in range(12)]
            revenue_data = []
            orders_data = []
            for i in range(12):
                month_start = year_start.replace(month=i+1)
                next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
                month_orders = Order.objects.filter(created_at__gte=month_start, created_at__lt=next_month)
                revenue_data.append(float(month_orders.aggregate(total=Sum('total'))['total'] or 0))
                orders_data.append(month_orders.count())
        else:
            # Daily data for today/week/month
            days = (now - start_date).days + 1
            labels = []
            revenue_data = []
            orders_data = []
            for i in range(days):
                day = start_date + timedelta(days=i)
                next_day = day + timedelta(days=1)
                day_orders = Order.objects.filter(created_at__gte=day, created_at__lt=next_day)
                labels.append(day.strftime('%a' if days <= 7 else '%d'))
                revenue_data.append(float(day_orders.aggregate(total=Sum('total'))['total'] or 0))
                orders_data.append(day_orders.count())

        # Top products
        top_products = Product.objects.filter(
            orderitem__order__created_at__gte=start_date
        ).annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:3]

        return {
            'revenue': float(revenue),
            'orders': order_count,
            'avg_order': float(avg_order),
            'customers': customer_count,
            'revenue_labels': labels,
            'revenue_data': revenue_data,
            'orders_data': orders_data,
            'top_products_labels': [p.name for p in top_products],
            'top_products_data': [float(p.total_sold or 0) for p in top_products],
        }

    # Get data for all ranges
    context = {
        'today_data': get_metrics(today_start),
        'week_data': get_metrics(week_start),
        'month_data': get_metrics(month_start),
        'year_data': get_metrics(year_start),
        'initial_range': 'month',  # Default view
    }
    return render(request, 'admin_analytic.html', context)

# >>> ADD THIS IMPORT AT THE VERY TOP OF views.py (with other imports)
import requests
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Cart, Order, OrderItem, ShippingAddress, Payment, logo
# <<< END IMPORTS

# ... [your existing views: login_view, signup_view, home, cart_view, etc.] ...

# ✅ CORRECTED PAYSTACK VIEWS — NO SPACES, NO TYPOS

def initiate_paystack_payment(request):
    if request.method != "POST":
        return redirect('cart')

    if not request.user.is_authenticated:
        messages.error(request, "Please log in to pay with Paystack.")
        return redirect('login')

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    cart_items = cart.items.all()
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = Decimal('5.00')
    tax = round(subtotal * Decimal('0.08'), 2)
    total_amount = subtotal + shipping_cost + tax

    amount_kobo = int(total_amount * 100)
    reference = str(uuid.uuid4())

    request.session['paystack_reference'] = reference
    request.session['paystack_cart_id'] = cart.id
    request.session['paystack_amount'] = str(total_amount)

    # ✅ FIXED: NO TRAILING SPACES IN URL
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": request.user.email,
        "amount": amount_kobo,
        "reference": reference,
        "callback_url": request.build_absolute_uri(reverse('verify_payment')),
    }

    try:
        # ✅ FIXED: 'requests.post', NOT 'request.post'
        response = requests.post(url, json=data, headers=headers, timeout=10)
        result = response.json()

        if result.get('status') and 'authorization_url' in result.get('data', {}):
            return redirect(result['data']['authorization_url'])
        else:
            msg = result.get('message', 'Unknown error from Paystack')
            messages.error(request, f"Payment failed: {msg}")
    except requests.exceptions.RequestException:
        messages.error(request, "Could not connect to Paystack. Please try again.")

    return redirect('cart')


def verify_payment(request):
    reference = request.GET.get('reference')
    if not reference or reference != request.session.get('paystack_reference'):
        messages.error(request, "Invalid payment reference.")
        return redirect('cart')

    # ✅ FIXED: NO EXTRA SPACES — proper f-string
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    try:
        # ✅ FIXED: 'requests.get', NOT 'request.get'
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()

        if result.get('status') and result['data'].get('status') == 'success':
            expected_amount = Decimal(request.session['paystack_amount'])
            paid_amount = Decimal(result['data']['amount']) / 100

            if abs(paid_amount - expected_amount) > Decimal('0.01'):
                messages.error(request, "Payment amount mismatch.")
                return redirect('cart')

            cart = get_object_or_404(Cart, id=request.session['paystack_cart_id'])
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                subtotal=sum(item.total_price for item in cart.items.all()),
                shipping_cost=Decimal('5.00'),
                tax=round(sum(item.total_price for item in cart.items.all()) * Decimal('0.08'), 2),
                total=expected_amount,
                status='paid',
                created_at=timezone.now()
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            ShippingAddress.objects.create(
                order=order,
                full_name=request.user.get_full_name() or request.user.username,
                address="Paid via Paystack",
                city="N/A", state="N/A", country="N/A", zip_code="0000", phone_number="0000000000"
            )

            Payment.objects.create(
                order=order,
                method='paystack',
                transaction_id=result['data']['reference'],
                amount=expected_amount,
                status='completed'
            )

            cart.delete()
            for key in ['paystack_reference', 'paystack_cart_id', 'paystack_amount']:
                request.session.pop(key, None)

            return redirect('order_confirmation', order_id=order.id)

        else:
            messages.error(request, "Payment was not successful.")
    except Exception:
        messages.error(request, "Verification failed. Please contact support.")

    return redirect('cart')


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confirmation.html', {
        'order': order,
        'logos': logo.objects.all()
    })