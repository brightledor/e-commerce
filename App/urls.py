from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_page'),
    path('signup/', views.signup_view, name='signup_page'),
    path('confirmed/', views.confirmed_view, name='confirmed_page'),
    path('home/', views.home, name="home"),
    path('shop/', views.shop, name='shop'),
    path("dashboard/",views.dashboard,name="dashboard"),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('shipping/', views.shipping_info_view, name='shipping_info'),
    path('payment/', views.payment_info_view, name='payment_info'),
    path('review/', views.review_order_view, name='review_order'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('admin_order/', views.admin_order, name= "admin_order"),
    path("admin_product/", views.admin_product, name="admin_product"),
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:product_id>/update/', views.update_product, name='update_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('admin_customer/',views.admin_customer,name="admin_customer"),
    path("admin_analytic",views.admin_analytic, name="admin_analytic"),
    path('paystack/initiate/', views.initiate_paystack_payment, name='initiate_paystack_payment'),
    path('paystack/verify/', views.verify_payment, name='verify_payment'),
]

