from django.urls import path
from . import views

app_name = 'executive_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('add-product/', views.add_product, name='add_product'),
    path('quick-update/<int:product_id>/', views.quick_update_product, name='quick_update_product'),
    path('adjust-stock/<int:product_id>/', views.adjust_stock, name='adjust_stock'),
    path('manual-order/', views.manual_order_create, name='manual_order_create'),
    path('log-payout/', views.log_dev_payout, name='log_dev_payout'), # Added here
    path('toggle-payment/<int:order_id>/', views.toggle_order_payment, name='toggle_payment'),
    path('toggle-delivery/<int:order_id>/', views.toggle_order_delivery, name='toggle_delivery'),
    path('add-expense/', views.add_expense, name='add_expense'),
]
