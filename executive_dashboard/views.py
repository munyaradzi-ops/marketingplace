from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils.text import slugify
from decimal import Decimal
import os

from products.models import Product, Category
from orders.models import Order, OrderItem
from .models import StockAuditLog, OperationalExpense, DeveloperPayout

@staff_member_required
def dashboard_home(request):
    # 1. Monetization Metrics Evaluation
    total_sales_revenue = OrderItem.objects.filter(order__paid=True).aggregate(
        total=Coalesce(Sum(F('price') * F('quantity'), output_field=DecimalField()), Decimal('0.00'))
    )['total']

    # Total 10% liability generated from paid sales
    total_dev_royalty_generated = total_sales_revenue * Decimal('0.10')

    # Total historical cash payouts already completed
    total_paid_to_dev = DeveloperPayout.objects.aggregate(
        total=Coalesce(Sum('amount_paid'), Decimal('0.00'))
    )['total']

    # Remaining balance awaiting transfer clearance
    dev_outstanding_balance = total_dev_royalty_generated - total_paid_to_dev

    total_wholesale_cost = StockAuditLog.objects.filter(change_quantity__gt=0).aggregate(
        total=Coalesce(Sum(F('change_quantity') * F('cost_per_unit'), output_field=DecimalField()), Decimal('0.00'))
    )['total']

    total_expenses = OperationalExpense.objects.aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    # Your net profit now accurately includes all historical operational overheads
    net_cash_flow = total_sales_revenue - total_dev_royalty_generated - total_wholesale_cost - total_expenses

    # 2. Inventory Metrics Analysis
    products = Product.objects.all().order_by('stock_count')
    categories = Category.objects.all()
    low_stock_items = products.filter(stock_count__lte=5)
    
    # 3. Operations History Lists
    all_orders = Order.objects.all().order_by('-created_at')
    expenses = OperationalExpense.objects.all().order_by('-date_incurred')[:10]
    dev_payout_history = DeveloperPayout.objects.all().order_by('-payout_date')[:10]

    context = {
        'total_revenue': total_sales_revenue,
        'total_dev_royalty': total_dev_royalty_generated,
        'total_paid_to_dev': total_paid_to_dev,
        'dev_outstanding': dev_outstanding_balance,
        'wholesale_cost': total_wholesale_cost,
        'total_expenses': total_expenses,
        'net_profit': net_cash_flow,
        'products': products,
        'categories': categories,
        'low_stock_items': low_stock_items,
        'all_orders': all_orders,
        'expenses': expenses,
        'payouts': dev_payout_history,
    }
    return render(request, 'executive_dashboard/home.html', context)

@staff_member_required
@require_POST
def log_dev_payout(request):
    amount = Decimal(request.POST.get('amount_paid', '0.00'))
    date = request.POST.get('payout_date')
    ref = request.POST.get('reference_note', '')

    DeveloperPayout.objects.create(
        amount_paid=amount,
        payout_date=date,
        reference_note=ref
    )
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def add_product(request):
    name = request.POST.get('name')
    category_id = request.POST.get('category')
    description = request.POST.get('description', '')
    price = Decimal(request.POST.get('price', '0.00'))
    stock_count = int(request.POST.get('stock_count', 0))
    image = request.FILES.get('image')

    category = get_object_or_404(Category, id=category_id)
    
    product = Product.objects.create(
        category=category,
        name=name,
        slug=slugify(name),
        description=description,
        price=price,
        stock_count=stock_count,
        image=image
    )

    if stock_count > 0:
        StockAuditLog.objects.create(
            product=product,
            change_quantity=stock_count,
            cost_per_unit=Decimal('0.00'),
            reason='RESTOCK'
        )
        
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def quick_update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.price = Decimal(request.POST.get('price', product.price))
    product.stock_count = int(request.POST.get('stock_count', product.stock_count))
    product.save()
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def adjust_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get('quantity', 0))
    cost = Decimal(request.POST.get('cost_per_unit', '0.00'))
    reason = request.POST.get('reason', 'RESTOCK')

    if reason in ['DAMAGE', 'CORRECTION'] and qty > 0:
        qty = -qty

    product.stock_count += qty
    product.save()

    StockAuditLog.objects.create(
        product=product,
        change_quantity=qty,
        cost_per_unit=cost,
        reason=reason
    )
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def manual_order_create(request):
    product_id = request.POST.get('product')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    
    order = Order.objects.create(
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        email=request.POST.get('email'),
        address=request.POST.get('address'),
        postal_code=request.POST.get('postal_code'),
        city=request.POST.get('city'),
        paid=request.POST.get('paid') == 'true',
        delivered=request.POST.get('delivered') == 'true'
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        price=product.price,
        quantity=quantity
    )
    
    if product.stock_count >= quantity:
        product.stock_count -= quantity
    else:
        product.stock_count = 0
    product.save()
    
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def toggle_order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.paid = not order.paid
    order.save()
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def toggle_order_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delivered = not order.delivered
    order.save()
    return redirect('executive_dashboard:home')

@staff_member_required
@require_POST
def add_expense(request):
    title = request.POST.get('title')
    amount = Decimal(request.POST.get('amount', '0.00'))
    category = request.POST.get('category')
    date_incurred = request.POST.get('date_incurred')

    OperationalExpense.objects.create(
        title=title,
        amount=amount,
        category=category,
        date_incurred=date_incurred
    )
    return redirect('executive_dashboard:home')
