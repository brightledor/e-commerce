from django.contrib import admin
from .models import Order, OrderItem,ShippingAddress,Category, Product,Payment, Testimonial, BlogPost, ContactMessage,logo,carousel


admin.site.register(carousel)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

admin.site.register(logo)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(OrderItem)
admin.site.register(Order)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_new', 'is_on_sale']
    list_filter = ['category', 'is_new', 'is_on_sale']
    # No need for custom update view — Django Admin handles it

    
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'title', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured', 'created_at')
    search_fields = ('customer_name', 'quote')
    list_editable = ('is_featured',)
    ordering = ('-created_at',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'slug')
    list_filter = ('published_date',)
    search_fields = ('title', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}  # auto-generate slug from title
    ordering = ('-published_date',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

