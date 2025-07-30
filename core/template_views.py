from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from users.models import User
from products.models import Product, Category
from products.tasks import process_product_video
import random
from orders.models import Order
from orders.serializers import OrderSerializer

def is_admin_or_staff(user):
    return user.is_authenticated and user.role in ['ADMIN', 'STAFF']

def template_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'END_USER')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists.')
        else:
            user = User.objects.create_user(email=email, password=password, role=role)
            user.is_active = True  # Auto-activate for template views
            user.save()
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('template_login')
    
    return render(request, 'register.html')

def template_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user and user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')

@login_required
def template_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('template_login')

@login_required
def dashboard(request):
    products = Product.objects.filter(uploaded_by=request.user).order_by('-created_at')
    
    if request.user.role == 'END_USER':
        status_filter = request.GET.get('status')
        if status_filter and status_filter != 'all':
            products = products.filter(status=status_filter)
    
    return render(request, 'dashboard.html', {'products': products})

@login_required
def add_product(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        video = request.FILES.get('video')
        
        try:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                name=name,
                description=description,
                category=category,
                uploaded_by=request.user,
                processing_status='UPLOADING'
            )
            
            if video:
                # Validate video size (20MB max)
                if video.size > 20 * 1024 * 1024:
                    messages.error(request, 'Video file must be ≤ 20MB.')
                    product.delete()
                    return render(request, 'add_product.html', {'categories': categories})
                
                product.temporary_video = video
                product.save()
                # Trigger async processing
                process_product_video.delay(product.id)
            else:
                product.processing_status = 'READY'
                product.save()
            
            messages.success(request, 'Product created successfully!')
            return redirect('dashboard')
            
        except Category.DoesNotExist:
            messages.error(request, 'Invalid category selected.')
    
    return render(request, 'add_product.html', {'categories': categories})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, uploaded_by=request.user)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        category_id = request.POST.get('category')
        video = request.FILES.get('video')
        
        try:
            product.category = Category.objects.get(id=category_id)
            
            if video:
                # Validate video size (20MB max)
                if video.size > 20 * 1024 * 1024:
                    messages.error(request, 'Video file must be ≤ 20MB.')
                    return render(request, 'add_product.html', {'product': product, 'categories': categories})
                
                product.temporary_video = video
                product.processing_status = 'UPLOADING'
                product.save()
                # Trigger async processing
                process_product_video.delay(product.id)
            else:
                product.save()
            
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard')
            
        except Category.DoesNotExist:
            messages.error(request, 'Invalid category selected.')
    
    return render(request, 'add_product.html', {'product': product, 'categories': categories})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, uploaded_by=request.user)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('dashboard')

@login_required
def generate_dummy(request):
    if request.method == 'POST':
        count = int(request.POST.get('count', 1))
        count = min(count, 50)  # Limit to 50
        
        # Get or create a default category
        category, created = Category.objects.get_or_create(
            name='Dummy Category',
            defaults={'description': 'Auto-generated category for dummy products'}
        )
        
        for i in range(count):
            Product.objects.create(
                name=f'Dummy Product {random.randint(1000, 9999)}',
                description=f'This is a dummy product created for testing purposes.',
                category=category,
                uploaded_by=request.user,
                processing_status='READY'
            )
        
        messages.success(request, f'Generated {count} dummy products successfully!')
    
    return redirect('dashboard') 

@login_required
def categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'categories.html', {'categories': categories})

@user_passes_test(is_admin_or_staff)
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Category.objects.filter(name=name).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Category created successfully!')
            return redirect('categories')
    
    return render(request, 'add_category.html')

@user_passes_test(is_admin_or_staff)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Check if name already exists (excluding current category)
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')
    
    return render(request, 'add_category.html', {'category': category})

@user_passes_test(is_admin_or_staff)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Check if category has products
    if category.products.exists():
        messages.error(request, f'Cannot delete category "{category.name}" because it has {category.products.count()} products. Move or delete the products first.')
    else:
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
    
    return redirect('categories') 

# Order Management Views
@login_required
def orders(request):
    if request.user.role in ['ADMIN', 'STAFF']:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def place_order(request):
    if request.user.role != 'END_USER':
        messages.error(request, 'Only end users can place orders.')
        return redirect('orders')
    
    approved_products = Product.objects.filter(status='APPROVED')
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('products')
        if not product_ids:
            messages.error(request, 'Please select at least one product.')
        else:
            order = Order.objects.create(user=request.user)
            order.products.set(product_ids)
            messages.success(request, f'Order #{order.id} placed successfully with {len(product_ids)} products!')
            return redirect('orders')
    
    return render(request, 'place_order.html', {'approved_products': approved_products})

@login_required
def order_detail(request, order_id):
    if request.user.role in ['ADMIN', 'STAFF']:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST' and request.user.role in ['ADMIN', 'STAFF']:
        new_status = request.POST.get('status')
        if new_status in ['PENDING', 'SUCCESS', 'CANCELLED']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
    
    return render(request, 'order_detail.html', {'order': order})

@login_required
def edit_order(request, order_id):
    if request.user.role not in ['ADMIN', 'STAFF']:
        messages.error(request, 'Only admin and staff can edit orders.')
        return redirect('orders')
    
    order = get_object_or_404(Order, id=order_id)
    return redirect('order_detail', order_id=order.id)

# Product Approval/Rejection Views
@user_passes_test(is_admin_or_staff)
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.status = 'APPROVED'
    product.save()
    messages.success(request, f'Product "{product.name}" has been approved.')
    return redirect('dashboard')

@user_passes_test(is_admin_or_staff)
def reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.status = 'REJECTED'
    product.save()
    messages.success(request, f'Product "{product.name}" has been rejected.')
    return redirect('dashboard') 