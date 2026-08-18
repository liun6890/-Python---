from django.urls import path
from . import views

urlpatterns = [
    path('auth/login', views.login),
    path('auth/logout', views.logout),
    path('auth/profile', views.profile),
    path('dashboard/stats', views.dashboard_stats),
    path('dashboard/inventory-pie', views.dashboard_inventory_pie),
    path('products', views.products),
    path('warehouses', views.warehouses),
    path('suppliers', views.suppliers),
    path('customers', views.customers),
    path('inbound/orders', views.inbound_orders),
    path('outbound/orders', views.outbound_orders),
    path('inventory/items', views.inventory_items),
    path('inventory/warning', views.inventory_warning),
    path('inventory/stocktaking', views.inventory_stocktaking),
    path('inventory/transfer', views.inventory_transfer),
    path('reports/dashboard', views.reports_dashboard),
    path('reports/daily', views.reports_daily),
    path('system/users', views.system_users),
    path('system/roles', views.system_roles),
    path('system/logs', views.system_logs),
]
