from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import (
    Product, Warehouse, Supplier, Customer,
    InboundOrder, InboundOrderItem,
    OutboundOrder, OutboundOrderItem,
    InventoryItem,
    SystemUser, SystemRole, SystemLog
)
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with realistic Chinese mock data including Order Items'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Clear existing data
        self.stdout.write('Clearing existing data...')
        User.objects.all().delete()
        SystemUser.objects.all().delete()
        Product.objects.all().delete()
        Warehouse.objects.all().delete()
        Supplier.objects.all().delete()
        Customer.objects.all().delete()
        InboundOrder.objects.all().delete()
        InboundOrderItem.objects.all().delete()
        OutboundOrder.objects.all().delete()
        OutboundOrderItem.objects.all().delete()
        InventoryItem.objects.all().delete()
        
        # 2. Create Users
        self.stdout.write('Creating users...')
        if not User.objects.filter(username='root').exists():
            User.objects.create_superuser('root', 'root@example.com', '123456')
            SystemUser.objects.create(username='root', role='admin', name='超级管理员', avatar='https://avatars.githubusercontent.com/u/1?v=4')
        
        if not User.objects.filter(username='manager').exists():
            User.objects.create_user('manager', 'manager@example.com', '123456')
            SystemUser.objects.create(username='manager', role='manager', name='仓库经理', avatar='https://avatars.githubusercontent.com/u/2?v=4')

        if not User.objects.filter(username='worker').exists():
            User.objects.create_user('worker', 'worker@example.com', '123456')
            SystemUser.objects.create(username='worker', role='operator', name='仓库操作员', avatar='https://avatars.githubusercontent.com/u/3?v=4')

        # 3. Warehouses
        self.stdout.write('Creating warehouses...')
        warehouses = [
            {'code': 'WH-SH-01', 'name': '上海主配送中心', 'address': '上海市浦东新区物流大道888号', 'contact': '张先生', 'phone': '13800138000'},
            {'code': 'WH-BJ-01', 'name': '北京分仓', 'address': '北京市顺义区机场路66号', 'contact': '李女士', 'phone': '13900139000'},
            {'code': 'WH-SZ-01', 'name': '深圳快速响应中心', 'address': '深圳市南山区科技园12号', 'contact': '王先生', 'phone': '13700137000'},
        ]
        
        wh_objs = []
        for wh in warehouses:
            obj, created = Warehouse.objects.get_or_create(code=wh['code'], defaults=wh)
            wh_objs.append(obj)

        # 4. Suppliers
        self.stdout.write('Creating suppliers...')
        suppliers = [
            {'name': '全球科技电子有限公司', 'contact': '刘强', 'phone': '021-12345678', 'rating': 5},
            {'name': '办公优选有限公司', 'contact': '陈美', 'phone': '010-87654321', 'rating': 4},
            {'name': '精品家具制造厂', 'contact': '黄伟', 'phone': '0755-11223344', 'rating': 4},
            {'name': '零件解决方案公司', 'contact': '周杰', 'phone': '020-99887766', 'rating': 3},
        ]
        
        sup_objs = []
        for sup in suppliers:
            obj, created = Supplier.objects.get_or_create(name=sup['name'], defaults=sup)
            sup_objs.append(obj)

        # 5. Customers
        self.stdout.write('Creating customers...')
        customers = [
            {'name': '科技连锁店A', 'contact': '店长', 'phone': '13500001111', 'address': '购物中心A座3层', 'credit_limit': 50000},
            {'name': '电商平台B', 'contact': '采购部', 'phone': '13600002222', 'address': '电商产业园C栋', 'credit_limit': 100000},
            {'name': '企业客户C', 'contact': '行政部', 'phone': '13300003333', 'address': 'CBD大厦25层', 'credit_limit': 200000},
        ]
        
        cust_objs = []
        for cust in customers:
            obj, created = Customer.objects.get_or_create(name=cust['name'], defaults=cust)
            cust_objs.append(obj)

        # 6. Products
        self.stdout.write('Creating products...')
        products = [
            {'sku_code': 'ELEC-001', 'spu_name': '无线人体工学鼠标', 'category': '电子产品', 'unit': '个', 'safety_stock': 50, 'barcode': '6900000000001'},
            {'sku_code': 'ELEC-002', 'spu_name': '机械键盘 RGB版', 'category': '电子产品', 'unit': '个', 'safety_stock': 30, 'barcode': '6900000000002'},
            {'sku_code': 'ELEC-003', 'spu_name': '27英寸 4K 显示器', 'category': '电子产品', 'unit': '台', 'safety_stock': 20, 'barcode': '6900000000003'},
            {'sku_code': 'FURN-001', 'spu_name': '网面办公椅', 'category': '家具', 'unit': '张', 'safety_stock': 10, 'barcode': '6900000000004'},
            {'sku_code': 'FURN-002', 'spu_name': '电动升降桌', 'category': '家具', 'unit': '张', 'safety_stock': 5, 'barcode': '6900000000005'},
            {'sku_code': 'SUPP-001', 'spu_name': 'A4 复印纸 (500张)', 'category': '办公用品', 'unit': '包', 'safety_stock': 100, 'barcode': '6900000000006'},
            {'sku_code': 'SUPP-002', 'spu_name': '圆珠笔 (黑色, 12支装)', 'category': '办公用品', 'unit': '盒', 'safety_stock': 50, 'barcode': '6900000000007'},
        ]
        
        prod_objs = []
        for prod in products:
            obj, created = Product.objects.get_or_create(sku_code=prod['sku_code'], defaults=prod)
            prod_objs.append(obj)

        # 7. Inventory (Initial Stock)
        self.stdout.write('Creating inventory...')
        for prod in prod_objs:
            for wh in wh_objs:
                # Randomize stock
                qty = random.randint(10, 200)
                locked = random.randint(0, 5)
                InventoryItem.objects.get_or_create(
                    product_sku=prod.sku_code,
                    warehouse_code=wh.code,
                    defaults={
                        'location_code': f'A-{random.randint(1,10)}-{random.randint(1,5)}',
                        'quantity': qty,
                        'locked_qty': locked,
                        'batch_no': f'BATCH-{timezone.now().strftime("%Y%m%d")}-{random.randint(100,999)}'
                    }
                )

        # 8. Inbound Orders
        self.stdout.write('Creating inbound orders...')
        inbound_statuses = ['草稿', '待审核', '已审核', '已收货', '已完成', '已驳回']
        for i in range(15):
            status = random.choice(inbound_statuses)
            supplier = random.choice(sup_objs)
            wh = random.choice(wh_objs)
            reject_reason = '数量超出合同范围' if status == '已驳回' else None
            order = InboundOrder.objects.create(
                order_no=f'IN-{timezone.now().strftime("%Y%m%d")}-{i+1000}',
                supplier_name=supplier.name,
                warehouse_code=wh.code,
                status=status,
                planned_date=timezone.now().date() + timedelta(days=random.randint(-10, 10)),
                remark='计划入库',
                reject_reason=reject_reason
            )
            
            # Create Items for this order
            num_items = random.randint(1, 3)
            selected_products = random.sample(prod_objs, num_items)
            for prod in selected_products:
                planned_qty = random.randint(10, 100)
                received_qty = 0
                putaway_qty = 0
                item_status = '草稿'
                location_code = None
                if status in ['已收货', '已完成']:
                    received_qty = random.randint(1, planned_qty)
                    item_status = '已收货'
                if status == '已完成':
                    putaway_qty = received_qty
                    item_status = '已上架'
                    location_code = f'A-{random.randint(1,10)}-{random.randint(1,5)}'
                InboundOrderItem.objects.create(
                    order=order,
                    product_sku=prod.sku_code,
                    quantity=planned_qty,
                    received_qty=received_qty,
                    putaway_qty=putaway_qty,
                    location_code=location_code,
                    status=item_status
                )

        # 9. Outbound Orders
        self.stdout.write('Creating outbound orders...')
        outbound_statuses = ['草稿', '待审核', '已审核', '待拣货', '已发货', '已完成', '已驳回']
        for i in range(15):
            status = random.choice(outbound_statuses)
            customer = random.choice(cust_objs)
            wh = random.choice(wh_objs)
            reject_reason = '客户信息不完整' if status == '已驳回' else None
            order = OutboundOrder.objects.create(
                order_no=f'OUT-{timezone.now().strftime("%Y%m%d")}-{i+1000}',
                customer_name=customer.name,
                warehouse_code=wh.code,
                status=status,
                planned_date=timezone.now().date() + timedelta(days=random.randint(-5, 15)),
                remark='计划出库',
                reject_reason=reject_reason
            )
            
            # Create Items for this order
            num_items = random.randint(1, 3)
            selected_products = random.sample(prod_objs, num_items)
            for prod in selected_products:
                OutboundOrderItem.objects.create(
                    order=order,
                    product_sku=prod.sku_code,
                    quantity=random.randint(5, 50)
                )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with realistic Chinese mock data and Order Items!'))
