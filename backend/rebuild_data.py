import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from api.models import (
    Product, Warehouse, Supplier, Customer,
    InboundOrder, InboundOrderItem,
    OutboundOrder, OutboundOrderItem,
    InventoryItem, InventoryStocktaking, InventoryTransfer,
    SystemUser, SystemRole, SystemLog
)
from django.contrib.auth.models import User

def rebuild_data():
    print(">>> 1. Clearing Database...")
    SystemLog.objects.all().delete()
    InventoryTransfer.objects.all().delete()
    InventoryStocktaking.objects.all().delete()
    InventoryItem.objects.all().delete()
    OutboundOrderItem.objects.all().delete()
    OutboundOrder.objects.all().delete()
    InboundOrderItem.objects.all().delete()
    InboundOrder.objects.all().delete()
    Customer.objects.all().delete()
    Supplier.objects.all().delete()
    Warehouse.objects.all().delete()
    Product.objects.all().delete()
    # Users/Roles kept or re-created? Let's keep USERS dict logic in views but models might be used
    SystemUser.objects.all().delete()
    SystemRole.objects.all().delete()
    User.objects.all().delete() # Clear Django Users

    print(">>> 2. Creating System Data...")
    # Create Django Superuser for JWT Auth
    User.objects.create_superuser('admin', 'admin@example.com', '123456')
    print("    - Created Django superuser: admin / 123456")

    roles = ['admin', 'manager', 'operator', 'viewer']
    for r in roles:
        SystemRole.objects.create(name=r)
    
    users = [
        {'username': 'admin', 'role': 'admin', 'name': 'Admin'},
        {'username': 'manager', 'role': 'manager', 'name': 'Manager'},
        {'username': 'operator', 'role': 'operator', 'name': 'Operator'},
        {'username': 'viewer', 'role': 'viewer', 'name': 'Viewer'},
    ]
    for u in users:
        SystemUser.objects.create(
            username=u['username'],
            role=u['role'],
            name=u['name'],
            avatar='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
        )
        # Also create Django users for them if not admin
        if u['username'] != 'admin':
            User.objects.create_user(u['username'], '', '123456')

    print(">>> 3. Creating Warehouses...")
    wh_main = Warehouse.objects.create(
        name="主仓库",
        code="WH-MAIN-01",
        address="上海市浦东新区物流园区",
        contact="张经理",
        phone="13800138000"
    )
    wh_sub = Warehouse.objects.create(
        name="分仓库",
        code="WH-SUB-01",
        address="北京市闵行区",
        contact="李主管",
        phone="13900139000"
    )

    print(">>> 4. Creating Products...")
    products = [
        {'sku': 'ELEC-001', 'name': '无线鼠标', 'cat': '电子产品', 'price': 50, 'unit': '个'},
        {'sku': 'ELEC-002', 'name': '机械键盘', 'cat': '电子产品', 'price': 300, 'unit': '个'},
        {'sku': 'OFFICE-001', 'name': 'A4打印纸', 'cat': '办公用品', 'price': 20, 'unit': '箱'},
        {'sku': 'OFFICE-002', 'name': '订书机', 'cat': '办公用品', 'price': 15, 'unit': '个'},
        {'sku': 'FOOD-001', 'name': '速溶咖啡', 'cat': '食品', 'price': 40, 'unit': '盒'},
    ]
    
    db_products = []
    for p in products:
        prod = Product.objects.create(
            sku_code=p['sku'],
            spu_name=p['name'],
            category=p['cat'],
            unit=p['unit'],
            safety_stock=10,
            barcode=f"BAR-{p['sku']}"
        )
        db_products.append(prod)

    print(">>> 5. Creating Partners...")
    Supplier.objects.create(name="联想供应商", contact="王五", phone="13600000001", rating=5)
    Supplier.objects.create(name="晨光文具", contact="赵六", phone="13600000002", rating=4)
    Customer.objects.create(name="科技公司A", contact="孙七", phone="13700000001", address="张江高科")
    Customer.objects.create(name="贸易公司B", contact="周八", phone="13700000002", address="漕河泾")

    print(">>> 6. Initializing Inventory (Simulating First Putaway)...")
    # Simulate putaway logic: create 10 slots for ELEC-001 in WH-MAIN-01
    # Item 1: ELEC-001 in Main Warehouse (50 items) -> Shelf 01
    # Slots A-01-01 to A-01-10
    for i in range(1, 11):
        loc = f"A-01-{str(i).zfill(2)}"
        qty = 0
        if i == 1: qty = 50 # Fill first slot
        InventoryItem.objects.create(
            product_sku='ELEC-001',
            warehouse_code='WH-MAIN-01',
            location_code=loc,
            quantity=qty,
            locked_qty=0
        )
        
    # Item 2: OFFICE-001 in Main Warehouse (150 items) -> Shelf 02
    # Slots A-02-01 to A-02-10
    for i in range(1, 11):
        loc = f"A-02-{str(i).zfill(2)}"
        qty = 0
        if i == 1: qty = 100
        if i == 2: qty = 50
        InventoryItem.objects.create(
            product_sku='OFFICE-001',
            warehouse_code='WH-MAIN-01',
            location_code=loc,
            quantity=qty,
            locked_qty=0
        )

    print(">>> 7. Creating Orders...")
    # Inbound Order (Completed)
    io = InboundOrder.objects.create(
        order_no=f"IN-{timezone.now().strftime('%Y%m%d')}-001",
        supplier_name="联想供应商",
        warehouse_code="WH-MAIN-01",
        status="已完成",
        planned_date=timezone.now().date()
    )
    InboundOrderItem.objects.create(order=io, product_sku='ELEC-001', quantity=50, received_qty=50, putaway_qty=50, location_code="A-01-01", status="已上架")
    
    # Inbound Order (Pending)
    io2 = InboundOrder.objects.create(
        order_no=f"IN-{timezone.now().strftime('%Y%m%d')}-002",
        supplier_name="晨光文具",
        warehouse_code="WH-MAIN-01",
        status="待审核",
        planned_date=timezone.now().date() + timedelta(days=1)
    )
    InboundOrderItem.objects.create(order=io2, product_sku='OFFICE-002', quantity=200)

    print(">>> Data Rebuild Complete!")

if __name__ == "__main__":
    rebuild_data()
