import json
import time
import secrets
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from .models import (
    Product, Warehouse, Supplier, Customer,
    InboundOrder, InboundOrderItem,
    OutboundOrder, OutboundOrderItem,
    InventoryItem, InventoryStocktaking, InventoryTransfer,
    SystemUser, SystemRole, SystemLog
)

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Legacy USERS and TOKENS are removed
# USERS = ...
# PASSWORD = ...
# TOKENS = ...

DATA = {
    'products': [],
    'warehouses': [],
    'suppliers': [],
    'customers': [],
    'inbound_orders': [],
    'outbound_orders': [],
    'inventory_items': [],
    'system_users': [], # Dynamic now
    'system_roles': [
        {'id': 1, 'name': 'admin'},
        {'id': 2, 'name': 'manager'},
        {'id': 3, 'name': 'operator'},
        {'id': 4, 'name': 'viewer'},
    ],
    'system_logs': [],
}


def json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return {}


def resp_ok(data=None, message='success'):
    return JsonResponse({'code': 200, 'message': message, 'data': data})


def resp_err(message='error', code=400):
    return JsonResponse({'code': code, 'message': message}, status=200)


def require_auth(request):
    try:
        # Manually invoke DRF's JWT auth
        jwt_auth = JWTAuthentication()
        # authenticate() returns (user, token) or None
        # It expects Authorization: Bearer <token>
        auth_result = jwt_auth.authenticate(request)
        if auth_result is None:
             return None, resp_err('未提供Token', 401)
        user, token = auth_result
        
        # Convert to dict format expected by legacy views
        sys_user = SystemUser.objects.filter(username=user.username).first()
        user_dict = {
            'id': user.id,
            'username': user.username,
            'role': sys_user.role if sys_user else 'viewer', 
            'name': sys_user.name if sys_user else user.username,
            'avatar': sys_user.avatar if sys_user else ''
        }
        return user_dict, None
    except AuthenticationFailed:
        return None, resp_err('Token无效或已过期', 401)
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        return None, resp_err('认证失败', 401)


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return resp_err('方法不允许', 405)
    body = json_body(request)
    username = body.get('username')
    password = body.get('password')
    
    if not username or not password:
        return resp_err('用户名或密码错误', 400)
        
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        # Fetch extra info
        sys_user = SystemUser.objects.filter(username=username).first()
        user_data = {
            'id': user.id,
            'username': user.username,
            'role': sys_user.role if sys_user else 'viewer',
            'name': sys_user.name if sys_user else user.username,
            'avatar': sys_user.avatar if sys_user else 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
        }
        
        return resp_ok({
            'token': str(refresh.access_token),
            'user': user_data
        })
    else:
        return resp_err('用户名或密码错误', 400)


@csrf_exempt
def logout(request):
    # JWT is stateless, client just drops token
    return resp_ok()


def profile(request):
    user, err = require_auth(request)
    if err:
        return err
    return resp_ok(user)


def dashboard_stats(request):
    try:
        user, err = require_auth(request)
        if err:
            return err
        
        today = timezone.localdate()
        start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
        
        # Real Stats - Sum of quantities
        inbound_today = InboundOrderItem.objects.filter(
            order__created_at__range=(start_of_day, end_of_day)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        outbound_today = OutboundOrderItem.objects.filter(
            order__created_at__range=(start_of_day, end_of_day)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # inventory_amount removed as we don't have price info
        # Use SKU count instead or total items
        sku_count = Product.objects.filter(is_active=True).count()
        
        # Real Tasks
        # Inbound: status='待收货' or '已审核' (ready to receive)
        inbound_tasks = InboundOrder.objects.filter(status__in=['待收货', '已审核']).order_by('created_at')[:5]
        inbound_tasks_list = []
        for t in inbound_tasks:
            inbound_tasks_list.append({
                'id': t.order_no,
                'supplier': t.supplier_name,
                'status': t.status
            })
            
        # Outbound: status='待拣货' or '已审核' (ready to pick)
        picking_tasks = OutboundOrder.objects.filter(status__in=['待拣货', '已审核']).order_by('created_at')[:5]
        picking_tasks_list = []
        for t in picking_tasks:
            picking_tasks_list.append({
                'id': t.order_no,
                'customer': t.customer_name,
                'status': t.status
            })

        # Trend 7d (Real data) for Dashboard Chart
        trend_7d = []
        for i in range(6, -1, -1):
            date = today - datetime.timedelta(days=i)
            start = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
            end = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))
            
            in_count = InboundOrderItem.objects.filter(
                order__created_at__range=(start, end)
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            out_count = OutboundOrderItem.objects.filter(
                order__created_at__range=(start, end)
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            trend_7d.append({
                'date': date.isoformat(),
                'inbound': in_count,
                'outbound': out_count
            })

        data = {
            'inbound_today': inbound_today,
            'outbound_today': outbound_today,
            'sku_count': sku_count,
            'trend_7d': trend_7d,
            'inbound_tasks': inbound_tasks_list,
            'picking_tasks': picking_tasks_list,
        }
        return resp_ok(data)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error('dashboard_stats error', exc_info=True)
        return resp_err('服务器内部错误', 500)


def dashboard_inventory_pie(request):
    user, err = require_auth(request)
    if err:
        return err
    warehouse_code = request.GET.get('warehouse_code')
    product_sku = request.GET.get('product_sku')
    qs = InventoryItem.objects.all()
    if warehouse_code:
        qs = qs.filter(warehouse_code=warehouse_code)
    if product_sku:
        # If product is selected, show distribution across warehouses
        # Use exact match for dropdown selection
        qs = qs.filter(product_sku=product_sku)
        data = qs.values('warehouse_code').annotate(total=Sum('quantity')).order_by('-total')
        warehouses = dict(Warehouse.objects.values_list('code', 'name'))
        result = []
        for item in data:
            code = item['warehouse_code']
            name = warehouses.get(code, code)
            if item['total'] > 0:
                result.append({
                    'name': name,
                    'value': item['total']
                })
    else:
        # Default: Show product distribution (in selected warehouse or globally)
        data = qs.values('product_sku').annotate(total=Sum('quantity')).order_by('-total')

        # Map SKU to Name（仅查询需要的两个字段）
        products = dict(Product.objects.values_list('sku_code', 'spu_name'))

        result = []
        for item in data:
            sku = item['product_sku']
            name = products.get(sku, sku)
            if item['total'] > 0:
                result.append({
                    'name': name,
                    'value': item['total']
                })
    return resp_ok(result)


def _safe_page_params(request):
    """解析分页参数，非法值回退到默认值，page_size 上限 200。"""
    try:
        page = int(request.GET.get('page', '1'))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = int(request.GET.get('pageSize', '10'))
        if page_size < 1:
            page_size = 10
        if page_size > 200:
            page_size = 200
    except (ValueError, TypeError):
        page_size = 10
    return page, page_size


def paginate(items, request):
    page, page_size = _safe_page_params(request)
    start = (page - 1) * page_size
    end = start + page_size
    return {'list': items[start:end], 'total': len(items), 'page': page, 'pageSize': page_size}


def paginate_qs(qs, request):
    page, page_size = _safe_page_params(request)
    start = (page - 1) * page_size
    end = start + page_size
    total = qs.count()
    return qs[start:end], total, page, page_size


def product_to_dict(item):
    created_at = item.created_at
    if created_at and isinstance(created_at, datetime.datetime):
        created_at = timezone.localtime(created_at)
        
    updated_at = item.updated_at
    if updated_at and isinstance(updated_at, datetime.datetime):
        updated_at = timezone.localtime(updated_at)

    return {
        'id': item.id,
        'sku_code': item.sku_code,
        'spu_name': item.spu_name,
        'category': item.category,
        'unit': item.unit,
        'safety_stock': item.safety_stock,
        'barcode': item.barcode,
        'is_active': item.is_active,
        'created_at': created_at.isoformat() if created_at else None,
        'updated_at': updated_at.isoformat() if updated_at else None,
    }


def model_to_dict(item, fields):
    data = {'id': item.id}
    for f in fields:
        val = getattr(item, f)
        if isinstance(val, datetime.datetime):
            val = timezone.localtime(val)
        if hasattr(val, 'isoformat'):
            val = val.isoformat()
        data[f] = val
    return data


def crud_model(request, model_cls, fields, order_by='-id', search_fields=None):
    user, err = require_auth(request)
    if err:
        return err
    if request.method == 'GET':
        qs = model_cls.objects.all().order_by(order_by)
        keyword = request.GET.get('keyword')
        if keyword and search_fields:
            cond = Q()
            for f in search_fields:
                cond |= Q(**{f'{f}__icontains': keyword})
            qs = qs.filter(cond)
        items, total, page, page_size = paginate_qs(qs, request)
        data = {
            'list': [model_to_dict(i, fields) for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size,
        }
        return resp_ok(data)
    if request.method == 'POST':
        body = json_body(request)
        payload = {f: body.get(f) for f in fields if f in body}
        item = model_cls.objects.create(**payload)
        return resp_ok(model_to_dict(item, fields))
    if request.method in ['PUT', 'PATCH']:
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        try:
            item = model_cls.objects.get(id=item_id)
        except model_cls.DoesNotExist:
            return resp_err('未找到', 404)
        for f in fields:
            if f in body:
                setattr(item, f, body.get(f))
        item.save()
        return resp_ok(model_to_dict(item, fields))
    if request.method == 'DELETE':
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        model_cls.objects.filter(id=item_id).delete()
        return resp_ok()
    return resp_err('方法不允许', 405)


def crud_collection(request, key):
    user, err = require_auth(request)
    if err:
        return err
    if request.method == 'GET':
        return resp_ok(paginate(DATA[key], request))
    if request.method == 'POST':
        body = json_body(request)
        body['id'] = int(time.time() * 1000)
        DATA[key].append(body)
        return resp_ok(body)
    if request.method in ['PUT', 'PATCH']:
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        for i, item in enumerate(DATA[key]):
            if item.get('id') == item_id:
                DATA[key][i] = {**item, **body}
                return resp_ok(DATA[key][i])
        return resp_err('未找到', 404)
    if request.method == 'DELETE':
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        DATA[key] = [i for i in DATA[key] if i.get('id') != item_id]
        return resp_ok()
    return resp_err('方法不允许', 405)


@csrf_exempt
def products(request):
    user, err = require_auth(request)
    if err:
        return err
    if request.method == 'GET':
        qs = Product.objects.all().order_by('-id')
        keyword = request.GET.get('keyword')
        if keyword:
            qs = qs.filter(Q(sku_code__icontains=keyword) | Q(spu_name__icontains=keyword))
        items, total, page, page_size = paginate_qs(qs, request)
        data = {
            'list': [product_to_dict(i) for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size,
        }
        return resp_ok(data)
    if request.method == 'POST':
        body = json_body(request)
        item = Product.objects.create(
            sku_code=body.get('sku_code', ''),
            spu_name=body.get('spu_name', ''),
            category=body.get('category'),
            unit=body.get('unit'),
            safety_stock=body.get('safety_stock') or 0,
            barcode=body.get('barcode'),
            is_active=body.get('is_active', True),
        )
        return resp_ok(product_to_dict(item))
    if request.method in ['PUT', 'PATCH']:
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        try:
            item = Product.objects.get(id=item_id)
        except Product.DoesNotExist:
            return resp_err('未找到', 404)
        for field in ['sku_code', 'spu_name', 'category', 'unit', 'safety_stock', 'barcode', 'is_active']:
            if field in body:
                setattr(item, field, body.get(field))
        item.save()
        return resp_ok(product_to_dict(item))
    if request.method == 'DELETE':
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        Product.objects.filter(id=item_id).delete()
        return resp_ok()
    return resp_err('方法不允许', 405)


@csrf_exempt
def warehouses(request):
    return crud_model(request, Warehouse, ['name', 'code', 'address', 'contact', 'phone', 'is_active'], search_fields=['name', 'code'])


@csrf_exempt
def suppliers(request):
    return crud_model(request, Supplier, ['name', 'contact', 'phone', 'rating', 'is_active'], search_fields=['name', 'contact', 'phone'])


@csrf_exempt
def customers(request):
    user, err = require_auth(request)
    if err:
        return err
    return crud_model(request, Customer, ['name', 'contact', 'phone', 'address', 'credit_limit'], search_fields=['name', 'contact', 'phone'])


def get_order_dict(item, order_type='inbound'):
    fields = ['order_no', 'status', 'planned_date', 'warehouse_code', 'remark', 'reject_reason']
    if order_type == 'inbound':
        fields.append('supplier_name')
    else:
        fields.append('customer_name')
    
    data = model_to_dict(item, fields)
    if order_type == 'inbound':
        data['items'] = [
            {
                'id': i.id,
                'product_sku': i.product_sku,
                'quantity': i.quantity,
                'received_qty': i.received_qty,
                'putaway_qty': i.putaway_qty,
                'location_code': i.location_code,
                'status': i.status,
            }
            for i in item.items.all()
        ]
    else:
        data['items'] = [
            {
                'id': i.id,
                'product_sku': i.product_sku,
                'quantity': i.quantity,
            }
            for i in item.items.all()
        ]
    return data


def validate_order_items(items):
    if not isinstance(items, list) or not items:
        return False, '商品明细不能为空'
    for i in items:
        sku = i.get('product_sku')
        qty = i.get('quantity')
        if not sku:
            return False, '商品SKU不能为空'
        try:
            qty = int(qty)
        except Exception:
            return False, '商品数量必须为整数'
        if qty <= 0:
            return False, '商品数量必须大于0'
    return True, None


def validate_status_transition(flow, old_status, new_status):
    if not new_status or new_status == old_status:
        return True
    if flow == 'inbound':
        allowed = {
            '草稿': ['待审核', '已取消'],
            '待审核': ['已审核', '已驳回', '已取消'],
            '已审核': ['部分收货', '已收货', '已完成', '已取消'],
            '部分收货': ['部分收货', '已收货', '已完成', '已取消'],
            '已收货': ['部分上架', '已完成', '已取消'],
            '部分上架': ['部分上架', '已完成', '已取消'],
            '已驳回': ['草稿', '已取消', '待审核'],
            '已完成': [],
            '已取消': [],
        }
    else:
        allowed = {
            '草稿': ['待审核', '已取消'],
            '待审核': ['已审核', '已驳回', '已取消'],
            '已审核': ['拣货中', '已发货', '已取消'],
            '拣货中': ['已发货', '已取消'],
            '已发货': ['已完成'],
            '已完成': [],
            '已驳回': ['草稿', '已取消', '待审核'],
            '已取消': [],
        }
    return new_status in allowed.get(old_status, [])


def get_inventory_available_qty(product_sku, warehouse_code):
    from django.db.models import F
    result = InventoryItem.objects.filter(
        product_sku=product_sku, warehouse_code=warehouse_code
    ).aggregate(available=Sum(F('quantity') - F('locked_qty')))
    return result['available'] or 0


def lock_inventory(order_items, warehouse_code):
    """锁定库存，必须在 transaction.atomic() 内调用，使用行级锁防止并发超卖。"""
    # 先检查再锁定，全程持行级锁
    for order_item in order_items:
        inv_items = list(InventoryItem.objects.select_for_update().filter(
            product_sku=order_item.product_sku,
            warehouse_code=warehouse_code
        ))
        available_qty = sum(inv.quantity - inv.locked_qty for inv in inv_items)
        if available_qty < order_item.quantity:
            return False, f'库存不足，商品 {order_item.product_sku} 可用 {available_qty} (需求 {order_item.quantity})'

        remaining = order_item.quantity
        for inv in sorted(inv_items, key=lambda x: (x.location_code or '', x.id)):
            if remaining <= 0:
                break
            can_lock = inv.quantity - inv.locked_qty
            if can_lock > 0:
                lock_amount = min(can_lock, remaining)
                inv.locked_qty += lock_amount
                inv.save()
                remaining -= lock_amount

    return True, None


def release_locked_inventory(order_items, warehouse_code):
    """释放锁定库存，必须在 transaction.atomic() 内调用。"""
    for order_item in order_items:
        inv_items = list(InventoryItem.objects.select_for_update().filter(
            product_sku=order_item.product_sku,
            warehouse_code=warehouse_code
        ).order_by('location_code', 'id'))
        remaining = order_item.quantity
        for inv in inv_items:
            if remaining <= 0:
                break
            if inv.locked_qty > 0:
                release_amount = min(inv.locked_qty, remaining)
                inv.locked_qty -= release_amount
                inv.save()
                remaining -= release_amount


def deduct_inventory(order_items, warehouse_code):
    """扣减库存，必须在 transaction.atomic() 内调用，使用行级锁防止并发。"""
    for order_item in order_items:
        inv_items = list(InventoryItem.objects.select_for_update().filter(
            product_sku=order_item.product_sku,
            warehouse_code=warehouse_code
        ).order_by('location_code', 'id'))
        total_qty = sum(inv.quantity for inv in inv_items)
        if total_qty < order_item.quantity:
            return False, f'库存不足，商品 {order_item.product_sku} 现有 {total_qty}'

        remaining = order_item.quantity
        # 优先扣减已锁定部分
        for inv in inv_items:
            if remaining <= 0:
                break
            if inv.locked_qty > 0:
                deduct = min(inv.locked_qty, remaining)
                inv.locked_qty -= deduct
                inv.quantity -= deduct
                inv.save()
                remaining -= deduct

        # 扣减未锁定部分（直发或差异场景）
        if remaining > 0:
            for inv in inv_items:
                if remaining <= 0:
                    break
                if inv.quantity > 0:
                    deduct = min(inv.quantity, remaining)
                    inv.quantity -= deduct
                    inv.save()
                    remaining -= deduct

    return True, None


LOCATION_MAX_QTY = 100


def get_location_current_qty(warehouse_code, location_code):
    qs = InventoryItem.objects.filter(warehouse_code=warehouse_code, location_code=location_code)
    total = 0
    for inv in qs:
        total += inv.quantity
    return total


def location_has_other_sku(warehouse_code, location_code, product_sku):
    return InventoryItem.objects.filter(
        warehouse_code=warehouse_code,
        location_code=location_code
    ).exclude(product_sku=product_sku).filter(quantity__gt=0).exists()


def next_location_code(location_code):
    parts = location_code.split('-')
    if not parts:
        return 'A-01-01'
    last = parts[-1]
    if last.isdigit():
        width = len(last)
        num = int(last) + 1
        parts[-1] = str(num).zfill(width)
        return '-'.join(parts)
    return f'{location_code}-01'


def allocate_putaway(warehouse_code, product_sku, qty, preferred_location):
    # Check if inventory items exist for this product in this warehouse
    items_count = InventoryItem.objects.filter(
        product_sku=product_sku,
        warehouse_code=warehouse_code
    ).count()
    
    # If no items, initialize 10 dedicated slots
    if items_count == 0:
        existing_items = InventoryItem.objects.filter(warehouse_code=warehouse_code).values_list('location_code', flat=True)
        max_shelf = 0
        for code in existing_items:
            if not code or '-' not in code: continue
            parts = code.split('-')
            if len(parts) >= 2 and parts[1].isdigit():
                shelf = int(parts[1])
                if shelf > max_shelf:
                    max_shelf = shelf
        
        next_shelf = max_shelf + 1
        
        for i in range(1, 11):
            loc_code = f"A-{str(next_shelf).zfill(2)}-{str(i).zfill(2)}"
            InventoryItem.objects.create(
                product_sku=product_sku,
                warehouse_code=warehouse_code,
                location_code=loc_code,
                quantity=0,
                locked_qty=0
            )
            
    # Calculate total existing quantity
    current_total = InventoryItem.objects.filter(
        product_sku=product_sku,
        warehouse_code=warehouse_code
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    if current_total + qty > 1000:
        raise ValueError(f"超出总库位容量上限 (当前: {current_total}, 新增: {qty}, 上限: 1000)")

    allocations = []
    remaining = qty
    
    # Iterate through the 10 dedicated slots
    # Sort by location code to fill A-01-01 first, then A-01-02...
    slots = InventoryItem.objects.filter(
        product_sku=product_sku,
        warehouse_code=warehouse_code
    ).order_by('location_code')
    
    for slot in slots:
        if remaining <= 0:
            break
            
        space = LOCATION_MAX_QTY - slot.quantity
        if space > 0:
            put_qty = min(space, remaining)
            slot.quantity += put_qty
            slot.save()
            allocations.append({'location_code': slot.location_code, 'quantity': put_qty})
            remaining -= put_qty
            
    if remaining > 0:
        raise ValueError(f"库位已满，无法分配剩余 {remaining} 件商品")
        
    return allocations


def recommend_location(product_sku, warehouse_code):
    # Just return the first slot, logic is handled in allocate_putaway
    return 'A-01-01'


def calculate_putaway_allocation(warehouse_code, product_sku, qty, preferred_location):
    # This is for preview only, simulating the logic in allocate_putaway
    
    # Fetch existing (or simulate if empty)
    slots_data = []
    db_slots = InventoryItem.objects.filter(
        product_sku=product_sku,
        warehouse_code=warehouse_code
    ).order_by('location_code')
    
    if not db_slots.exists():
        # Simulate empty slots based on next available shelf
        # This is tricky because we can't easily know the next shelf without heavy query, 
        # but for preview, maybe we can assume a new shelf if it's new product.
        # But wait, if it's new product, allocate_putaway will create slots.
        # So here we should probably simulate what allocate_putaway does.
        
        existing_items = InventoryItem.objects.filter(warehouse_code=warehouse_code).values_list('location_code', flat=True)
        max_shelf = 0
        for code in existing_items:
            if not code or '-' not in code: continue
            parts = code.split('-')
            if len(parts) >= 2 and parts[1].isdigit():
                shelf = int(parts[1])
                if shelf > max_shelf:
                    max_shelf = shelf
        next_shelf = max_shelf + 1
        
        for i in range(1, 11):
            slots_data.append({
                'location_code': f"A-{str(next_shelf).zfill(2)}-{str(i).zfill(2)}",
                'quantity': 0
            })
    else:
        for s in db_slots:
            slots_data.append({
                'location_code': s.location_code,
                'quantity': s.quantity
            })
            
    current_total = sum(s['quantity'] for s in slots_data)
    if current_total + qty > 1000:
        # Just return empty or partial to indicate issue, but better not to raise in preview?
        # Let's just fill what we can
        pass

    allocations = []
    remaining = qty
    
    for slot in slots_data:
        if remaining <= 0:
            break
        
        space = LOCATION_MAX_QTY - slot['quantity']
        if space > 0:
            put_qty = min(space, remaining)
            allocations.append({'location_code': slot['location_code'], 'quantity': put_qty})
            remaining -= put_qty
            
    return allocations


@csrf_exempt
def inbound_orders(request):
    user, err = require_auth(request)
    if err:
        return err
    
    if request.method == 'GET':
        action = request.GET.get('action')
        if action == 'putaway_preview':
            wh_code = request.GET.get('warehouse_code')
            sku = request.GET.get('product_sku')
            qty = int(request.GET.get('quantity', 0))
            loc = request.GET.get('location_code')
            if not all([wh_code, sku, qty]):
                return resp_err('缺少参数', 400)
            allocations = calculate_putaway_allocation(wh_code, sku, qty, loc)
            return resp_ok({'allocations': allocations})
            
        if action == 'putaway_preview_batch':
            items_json = request.GET.get('items')
            if not items_json:
                return resp_err('缺少items参数', 400)
            try:
                items = json.loads(items_json)
            except Exception:
                return resp_err('items格式错误', 400)
                
            # items: [{product_sku, quantity, warehouse_code, location_code}]
            
            # We need to maintain a virtual state of occupied capacity
            # virtual_inventory: { (wh, loc): qty }
            # But wait, we need to know the capacity of each location.
            # Assuming max capacity 100 for all locations.
            
            # Since we can't easily mock DB queries, we will:
            # 1. Fetch current state for involved locations (or all relevant ones)
            # 2. Update a local state object as we iterate
            
            # Simplified approach:
            # Iterate items. For each item:
            #   Calculate allocation using standard logic BUT check against local 'reserved' state first.
            #   Add result to 'reserved' state.
            
            reserved_usage = {} # Key: (wh, loc), Value: used_qty (increment on top of DB)
            reserved_skus = {}  # Key: (wh, loc), Value: set(skus) - to track mixed SKU restriction
            
            all_results = []
            
            for item in items:
                wh_code = item.get('warehouse_code')
                sku = item.get('product_sku')
                qty = int(item.get('quantity', 0))
                loc = item.get('location_code')
                
                if not all([wh_code, sku, qty]):
                    continue
                    
                # Custom allocation logic that respects reserved_usage
                allocations = []
                
                # Use simplified logic matching new allocate_putaway
                # 1. Fetch current DB state for this SKU
                db_slots = InventoryItem.objects.filter(
                    product_sku=sku,
                    warehouse_code=wh_code
                ).order_by('location_code')
                
                slots_state = []
                if not db_slots.exists():
                    # Simulate empty slots - logic copied from calculate_putaway_allocation
                    existing_items = InventoryItem.objects.filter(warehouse_code=wh_code).values_list('location_code', flat=True)
                    max_shelf = 0
                    for code in existing_items:
                        if not code or '-' not in code: continue
                        parts = code.split('-')
                        if len(parts) >= 2 and parts[1].isdigit():
                            shelf = int(parts[1])
                            if shelf > max_shelf:
                                max_shelf = shelf
                    next_shelf = max_shelf + 1
                    
                    for i in range(1, 11):
                        slots_state.append({
                            'location_code': f"A-{str(next_shelf).zfill(2)}-{str(i).zfill(2)}",
                            'quantity': 0
                        })
                else:
                    for s in db_slots:
                        slots_state.append({
                            'location_code': s.location_code,
                            'quantity': s.quantity
                        })
                        
                # 2. Apply reserved usage from this batch
                for slot in slots_state:
                    key = (wh_code, slot['location_code'], sku) # Key needs sku now as locations are per-sku logically in this new model? 
                    # Actually, if we assume physical slots are shared but we are using "dedicated logic", 
                    # let's stick to the prompt: "for this product... 10 dedicated slots".
                    # So we just track usage by (wh, loc) is fine if locs are unique per sku? 
                    # No, locs are A-01-01. If multiple SKUs use A-01-01, we have a problem in this "dedicated" logic 
                    # UNLESS "dedicated" means "A-01-01 OF THIS SKU".
                    # Given the prompt "batch generate 10 dedicated slots... A-01-01 to A-01-10", 
                    # it strongly implies A-01-01 is reused across SKUs in this demo system.
                    # So reserved_usage should be keyed by (wh, loc, sku) to be safe?
                    # Or just (wh, loc) if we want to track capacity? 
                    # But the requirement says "dedicated slots", implies capacity is 100 PER SKU PER SLOT.
                    # So we should check capacity against (SKU, Slot).
                    
                    reserved = reserved_usage.get((wh_code, slot['location_code'], sku), 0)
                    slot['quantity'] += reserved
                    
                # 3. Allocate
                rem = qty
                for slot in slots_state:
                    if rem <= 0: break
                    
                    space = LOCATION_MAX_QTY - slot['quantity']
                    if space > 0:
                        put = min(space, rem)
                        allocations.append({'location_code': slot['location_code'], 'quantity': put})
                        
                        # Update reserved
                        key = (wh_code, slot['location_code'], sku)
                        reserved_usage[key] = reserved_usage.get(key, 0) + put
                        rem -= put
                
                for a in allocations:
                    all_results.append({
                        'product_sku': sku,
                        'location_code': a['location_code'],
                        'quantity': a['quantity']
                    })
                    
            return resp_ok({'allocations': all_results})

        qs = InboundOrder.objects.prefetch_related('items').order_by('-id')
        keyword = request.GET.get('keyword')
        status = request.GET.get('status')
        if keyword:
            qs = qs.filter(Q(order_no__icontains=keyword) | Q(supplier_name__icontains=keyword))
        if status:
            qs = qs.filter(status=status)

        items, total, page, page_size = paginate_qs(qs, request)
        data = {
            'list': [get_order_dict(i, 'inbound') for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size,
        }
        return resp_ok(data)
    
    if request.method == 'POST':
        body = json_body(request)
        items_data = body.get('items', [])
        valid, msg = validate_order_items(items_data)
        if not valid:
            return resp_err(msg, 400)
            
        # Validate capacity for each item
        warehouse_code = body.get('warehouse_code')
        for i_data in items_data:
            sku = i_data.get('product_sku')
            qty = int(i_data.get('quantity', 0))
            
            current_total = InventoryItem.objects.filter(
                product_sku=sku,
                warehouse_code=warehouse_code
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if current_total + qty > 1000:
                return resp_err(f"商品 {sku} 超出库存容量上限 (当前: {current_total}, 申请: {qty}, 上限: 1000)", 400)

        # 单号始终由后端生成，保证唯一性
        today_str = timezone.localdate().strftime('%Y%m%d')
        order_no = f"IN-{today_str}-{secrets.token_hex(3).upper()}"

        with transaction.atomic():
            item = InboundOrder.objects.create(
                order_no=order_no,
                supplier_name=body.get('supplier_name'),
                warehouse_code=body.get('warehouse_code'),
                planned_date=body.get('planned_date'),
                status=body.get('status') or '草稿',
                remark=body.get('remark'),
                reject_reason=None
            )
            for i_data in items_data:
                InboundOrderItem.objects.create(
                    order=item,
                    product_sku=i_data.get('product_sku'),
                    quantity=i_data.get('quantity', 1),
                    received_qty=0,
                    putaway_qty=0,
                    location_code=i_data.get('location_code'),
                    status='草稿'
                )
            
            SystemLog.objects.create(
                operator=user['username'],
                action='入库单创建',
                detail=f'创建入库单 {item.order_no}，包含 {len(items_data)} 个明细'
            )
        return resp_ok(get_order_dict(item, 'inbound'))
    
    if request.method in ['PUT', 'PATCH']:
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        try:
            item = InboundOrder.objects.get(id=item_id)
        except InboundOrder.DoesNotExist:
            return resp_err('未找到', 404)
        
        old_status = item.status
        action = body.get('action')
        new_status = body.get('status', old_status)
        if action == 'submit':
            new_status = '待审核'
        elif action == 'approve':
            new_status = '已审核'
        elif action == 'reject':
            new_status = '已驳回'
        elif action == 'cancel':
            new_status = '已取消'
        elif action == 'receive':
            new_status = '已收货'
        elif action == 'putaway':
            new_status = '已完成'
        if not validate_status_transition('inbound', old_status, new_status):
            return resp_err('状态流转不合法', 400)
        if 'items' in body:
            valid, msg = validate_order_items(body.get('items'))
            if not valid:
                return resp_err(msg, 400)
                
            # If updating items, validate capacity again (especially if quantity increased)
            # Note: This is a simplified check. Ideally we should diff with old items.
            # But since we replace all items, we can just check the new set against CURRENT inventory.
            # However, if this order was already approved/received, inventory might have been updated?
            # Usually edits are only allowed in Draft/Pending state where inventory hasn't been touched.
            if old_status in ['草稿', '待审核']:
                wh_code = body.get('warehouse_code', item.warehouse_code)
                for i_data in body['items']:
                    sku = i_data.get('product_sku')
                    qty = int(i_data.get('quantity', 0))
                    
                    current_total = InventoryItem.objects.filter(
                        product_sku=sku,
                        warehouse_code=wh_code
                    ).aggregate(total=Sum('quantity'))['total'] or 0
                    
                    if current_total + qty > 1000:
                        return resp_err(f"商品 {sku} 超出库存容量上限 (当前: {current_total}, 申请: {qty}, 上限: 1000)", 400)
        
        with transaction.atomic():
            for f in ['order_no', 'supplier_name', 'status', 'planned_date', 'warehouse_code', 'remark']:
                if f in body:
                    setattr(item, f, body.get(f))
            item.status = new_status
            if action == 'reject':
                item.reject_reason = body.get('reject_reason')
            if action in ['submit', 'approve']:
                item.reject_reason = None
            item.save()
            
            # Log System Operation
            log_action = {
                'submit': '入库单提交',
                'approve': '入库单审核',
                'reject': '入库单驳回',
                'cancel': '入库单取消',
                'receive': '入库单收货',
                'putaway': '入库单上架完成'
            }.get(action, '入库单更新')
            
            if action:
                SystemLog.objects.create(
                    operator=user['username'],
                    action=log_action,
                    detail=f'入库单 {item.order_no} 状态变更为 {new_status}'
                )
            
            if 'items' in body and action not in ['receive', 'putaway']:
                item.items.all().delete()
                for i_data in body['items']:
                    InboundOrderItem.objects.create(
                        order=item,
                        product_sku=i_data.get('product_sku'),
                        quantity=i_data.get('quantity', 1),
                        received_qty=0,
                        putaway_qty=0,
                        location_code=i_data.get('location_code'),
                        status='草稿'
                    )
            
            if action == 'receive':
                receive_items = body.get('receive_items', [])
                if not isinstance(receive_items, list) or not receive_items:
                    return resp_err('缺少收货明细', 400)
                for r in receive_items:
                    item_id = r.get('id')
                    received_qty = r.get('received_qty')
                    completion_status = r.get('completion_status') # 'completed' or 'partial'
                    reason = r.get('reason')
                    
                    if item_id is None or received_qty is None:
                        return resp_err('收货明细不完整', 400)
                    order_item = InboundOrderItem.objects.get(id=item_id, order=item)
                    received_qty = int(received_qty)
                    if received_qty < 0:
                        return resp_err('实收数量不能小于0', 400)
                    if received_qty > order_item.quantity:
                        return resp_err('实收数量不能超过计划数量', 400)
                    
                    order_item.received_qty = received_qty
                    
                    if completion_status == 'completed':
                         order_item.status = '已收货'
                    elif completion_status == 'partial':
                         order_item.status = '部分收货'
                    else:
                         # Fallback logic
                         order_item.status = '已收货' if received_qty >= order_item.quantity else '部分收货'
                         
                    if received_qty == 0: 
                        if completion_status == 'completed':
                            order_item.status = '已收货' # Completed with 0 qty (e.g. rejected all)
                        else:
                            order_item.status = '草稿'
                            
                    if reason:
                        order_item.reason = reason
                        
                    order_item.save()
                
                # Update main order status
                # Check if all items are '已收货' or '已完成'
                all_done = all(i.status in ['已收货', '已完成', '已上架', '部分上架'] for i in item.items.all())
                some_received = any(i.received_qty > 0 for i in item.items.all())
                
                if all_done:
                    item.status = '已收货'
                elif some_received:
                    item.status = '部分收货'
                else:
                    item.status = '已审核'
                item.save()
            
            if action == 'putaway':
                putaway_items = body.get('putaway_items', [])
                if not isinstance(putaway_items, list) or not putaway_items:
                    return resp_err('缺少上架明细', 400)
                wh_code = item.warehouse_code or 'WH-SH-01'
                for p in putaway_items:
                    item_id = p.get('id')
                    putaway_qty = p.get('putaway_qty')
                    location_code = p.get('location_code')
                    completion_status = p.get('completion_status') # 'completed' or 'partial'
                    reason = p.get('reason')
                    
                    if item_id is None or putaway_qty is None:
                        return resp_err('上架明细不完整', 400)
                    order_item = InboundOrderItem.objects.get(id=item_id, order=item)
                    putaway_qty = int(putaway_qty)
                    if putaway_qty < 0:
                        return resp_err('上架数量不能小于0', 400)
                    if putaway_qty > order_item.received_qty:
                        return resp_err('上架数量不能超过实收数量', 400)
                    
                    delta = putaway_qty - order_item.putaway_qty
                    if delta < 0:
                        return resp_err('上架数量不能回退', 400)
                    
                    if delta > 0:
                        if location_code and location_has_other_sku(wh_code, location_code, order_item.product_sku):
                            return resp_err('库位已存放其他商品，请选择其他库位', 400)
                        
                        preferred_loc = location_code or order_item.location_code or recommend_location(order_item.product_sku, wh_code)
                        allocations = allocate_putaway(wh_code, order_item.product_sku, delta, preferred_loc)
                        
                        loc_codes = [a['location_code'] for a in allocations]
                        existing_codes = []
                        if order_item.location_code:
                            existing_codes = [c.strip() for c in order_item.location_code.split(',') if c.strip()]
                        order_item.location_code = ','.join(list(dict.fromkeys(existing_codes + loc_codes)))
                    
                    order_item.putaway_qty = putaway_qty
                    
                    if completion_status == 'completed':
                        order_item.status = '已上架' # Means fully putaway/closed
                    elif completion_status == 'partial':
                        order_item.status = '部分上架'
                    else:
                        # Fallback
                        if order_item.putaway_qty >= order_item.received_qty and order_item.received_qty > 0:
                            order_item.status = '已上架'
                        elif order_item.putaway_qty > 0:
                            order_item.status = '部分上架'
                            
                    if reason:
                        order_item.reason = reason
                        
                    order_item.save()
                
                # Update main order status
                # Check if ALL items are fully putaway (status='已上架' or '已完成')
                all_items_done = all(
                    i.status in ['已上架', '已完成']
                    for i in item.items.all()
                )
                
                # Calculate totals for logging/status logic if needed
                total_recv = sum(i.received_qty for i in item.items.all())
                total_put = sum(i.putaway_qty for i in item.items.all())
                
                log_detail = f'入库单 {item.order_no} 执行上架'
                if all_items_done:
                    item.status = '已完成'
                    log_detail = f'入库单 {item.order_no} 全部上架完成'
                elif total_put > 0:
                    item.status = '部分上架'
                    log_detail = f'入库单 {item.order_no} 部分上架中'
                else:
                    pass
                
                # Enhanced logging with location info
                item_logs = []
                for pi in putaway_items:
                    oi = InboundOrderItem.objects.get(id=pi.get('id'))
                    item_logs.append(f"{oi.product_sku}({pi.get('putaway_qty')}件 -> {oi.location_code})")
                
                SystemLog.objects.create(
                    operator=user['username'],
                    action='入库上架',
                    detail=f"{log_detail}。明细: {'; '.join(item_logs)}"
                )
                item.save()

        return resp_ok(get_order_dict(item, 'inbound'))
    
    if request.method == 'DELETE':
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        InboundOrder.objects.filter(id=item_id).delete()
        return resp_ok()
    return resp_err('方法不允许', 405)


@csrf_exempt
def outbound_orders(request):
    user, err = require_auth(request)
    if err:
        return err
    
    if request.method == 'GET':
        qs = OutboundOrder.objects.prefetch_related('items').order_by('-id')
        keyword = request.GET.get('keyword')
        status = request.GET.get('status')
        if keyword:
            qs = qs.filter(Q(order_no__icontains=keyword) | Q(customer_name__icontains=keyword))
        if status:
            qs = qs.filter(status=status)

        items, total, page, page_size = paginate_qs(qs, request)
        data = {
            'list': [get_order_dict(i, 'outbound') for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size,
        }
        return resp_ok(data)
    
    if request.method == 'POST':
        body = json_body(request)
        items_data = body.get('items', [])
        valid, msg = validate_order_items(items_data)
        if not valid:
            return resp_err(msg, 400)
        # 单号始终由后端生成，保证唯一性
        today_str = timezone.localdate().strftime('%Y%m%d')
        order_no = f"OUT-{today_str}-{secrets.token_hex(3).upper()}"

        with transaction.atomic():
            item = OutboundOrder.objects.create(
                order_no=order_no,
                customer_name=body.get('customer_name'),
                warehouse_code=body.get('warehouse_code'),
                planned_date=body.get('planned_date'),
                status=body.get('status') or '草稿',
                remark=body.get('remark'),
                reject_reason=None
            )
            for i_data in items_data:
                OutboundOrderItem.objects.create(
                    order=item,
                    product_sku=i_data.get('product_sku'),
                    quantity=i_data.get('quantity', 1)
                )
            
            SystemLog.objects.create(
                operator=user['username'],
                action='出库单创建',
                detail=f'创建出库单 {item.order_no}，包含 {len(items_data)} 个明细'
            )
        return resp_ok(get_order_dict(item, 'outbound'))
    
    if request.method in ['PUT', 'PATCH']:
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        try:
            item = OutboundOrder.objects.get(id=item_id)
        except OutboundOrder.DoesNotExist:
            return resp_err('未找到', 404)
            
        old_status = item.status
        action = body.get('action')
        new_status = body.get('status', old_status)
        if action == 'submit':
            new_status = '待审核'
        elif action == 'approve':
            new_status = '已审核'
        elif action == 'reject':
            new_status = '已驳回'
        elif action == 'cancel':
            new_status = '已取消'
        if not validate_status_transition('outbound', old_status, new_status):
            return resp_err('状态流转不合法', 400)
        if 'items' in body:
            valid, msg = validate_order_items(body.get('items'))
            if not valid:
                return resp_err(msg, 400)
        
        try:
            with transaction.atomic():
                for f in ['order_no', 'customer_name', 'status', 'planned_date', 'warehouse_code', 'remark']:
                    if f in body:
                        setattr(item, f, body.get(f))
                item.status = new_status
                if action == 'reject':
                    item.reject_reason = body.get('reject_reason')
                if action in ['submit', 'approve']:
                    item.reject_reason = None
                item.save()
                
                if 'items' in body:
                    item.items.all().delete()
                    for i_data in body['items']:
                        OutboundOrderItem.objects.create(
                            order=item,
                            product_sku=i_data.get('product_sku'),
                            quantity=i_data.get('quantity', 1)
                        )
                
                wh_code = item.warehouse_code or 'WH-SH-01'

                if old_status == '待审核' and new_status == '已审核':
                    ok, msg = lock_inventory(item.items.all(), wh_code)
                    if not ok:
                        raise ValueError(msg)
                    
                    SystemLog.objects.create(
                        operator=user['username'],
                        action='出库审核',
                        detail=f'出库单 {item.order_no} 审核通过，锁定库存'
                    )

                if old_status in ['已审核', '拣货中'] and new_status in ['已驳回', '已取消']:
                    release_locked_inventory(item.items.all(), wh_code)
                    SystemLog.objects.create(
                        operator=user['username'],
                        action='出库撤销',
                        detail=f'出库单 {item.order_no} 撤销，释放锁定库存'
                    )

                if old_status == '已审核' and new_status == '拣货中':
                    item.status = '拣货中'
                    SystemLog.objects.create(
                        operator=user['username'],
                        action='出库拣货',
                        detail=f'出库单 {item.order_no} 开始拣货'
                    )

                if old_status != '已发货' and new_status == '已发货':
                    # Only allow shipping if status is '拣货中' or '已审核'
                    if old_status not in ['拣货中', '已审核']:
                         raise ValueError('必须先审核或拣货才能发货')
                         
                    ok, msg = deduct_inventory(item.items.all(), wh_code)
                    if not ok:
                        raise ValueError(msg)
                    total_qty = sum(i.quantity for i in item.items.all())
                    item.status = '已完成' # Mark as completed after shipping
                    SystemLog.objects.create(
                        operator=user['username'],
                        action='出库发货',
                        detail=f'出库单 {item.order_no} 发货完成，扣减库存 {total_qty}，状态更新为已完成'
                    )
        except ValueError as e:
            return resp_err(str(e), 400)

        return resp_ok(get_order_dict(item, 'outbound'))
    
    if request.method == 'DELETE':
        body = json_body(request)
        item_id = body.get('id')
        if not item_id:
            return resp_err('缺少 id', 400)
        OutboundOrder.objects.filter(id=item_id).delete()
        return resp_ok()
    return resp_err('方法不允许', 405)


@csrf_exempt
def inventory_items(request):
    user, err = require_auth(request)
    if err:
        return err
    
    if request.method == 'GET':
        qs = InventoryItem.objects.all().order_by('-id')

        # Filters
        product_sku = request.GET.get('product_sku')
        warehouse_code = request.GET.get('warehouse_code')
        location_code = request.GET.get('location_code')

        if product_sku:
            qs = qs.filter(product_sku__icontains=product_sku)
        if warehouse_code:
            qs = qs.filter(warehouse_code__icontains=warehouse_code)
        if location_code:
            qs = qs.filter(location_code__icontains=location_code)

        items, total, page, page_size = paginate_qs(qs, request)

        # Calculate available quantity (total - locked)
        products_map = {p.sku_code: p.safety_stock for p in Product.objects.all()}
        result_list = []
        for i in items:
            d = model_to_dict(i, ['product_sku', 'warehouse_code', 'location_code', 'quantity', 'locked_qty', 'batch_no'])
            d['available_qty'] = i.quantity - i.locked_qty
            d['safety_stock'] = products_map.get(i.product_sku, 0)
            result_list.append(d)

        data = {
            'list': result_list,
            'total': total,
            'page': page,
            'pageSize': page_size,
        }
        return resp_ok(data)

    return resp_err('库存查询仅支持GET请求')


def inventory_warning(request):
    user, err = require_auth(request)
    if err:
        return err
    
    # Get all products and their safety stock
    products_map = {p.sku_code: p.safety_stock for p in Product.objects.all()}
    
    # Aggregate inventory by (product_sku, warehouse_code)
    qs = InventoryItem.objects.values('product_sku', 'warehouse_code').annotate(
        total_qty=Sum('quantity'),
        total_locked=Sum('locked_qty')
    )

    product_sku = request.GET.get('product_sku')
    warehouse_code = request.GET.get('warehouse_code')
    if product_sku:
        qs = qs.filter(product_sku__icontains=product_sku)
    if warehouse_code:
        qs = qs.filter(warehouse_code__icontains=warehouse_code)

    # Filter by safety stock: only when available qty (total - locked) is below safety stock
    warning_list = []
    for item in qs:
        sku = item['product_sku']
        wh = item['warehouse_code']
        total_qty = item['total_qty']
        locked_qty = item['total_locked'] or 0
        available_qty = total_qty - locked_qty
        safety = products_map.get(sku, 0)

        if available_qty < safety:
            warning_list.append({
                'product_sku': sku,
                'warehouse_code': wh,
                'quantity': total_qty,
                'locked_qty': locked_qty,
                'available_qty': available_qty,
                'safety_stock': safety,
                'shortage': safety - available_qty
            })
            
    # Manual pagination
    total = len(warning_list)
    page = int(request.GET.get('page', '1'))
    page_size = int(request.GET.get('pageSize', '10'))
    start = (page - 1) * page_size
    end = start + page_size
    items = warning_list[start:end]

    data = {
        'list': items,
        'total': total,
        'page': page,
        'pageSize': page_size,
    }
    return resp_ok(data)


@csrf_exempt
def inventory_stocktaking(request):
    user, err = require_auth(request)
    if err:
        return err
        
    if request.method == 'GET':
        # Stocktaking list logic
        qs = InventoryStocktaking.objects.all().order_by('-id')
        
        product_sku = request.GET.get('product_sku')
        warehouse_code = request.GET.get('warehouse_code')
        
        if product_sku:
            qs = qs.filter(product_sku__icontains=product_sku)
        if warehouse_code:
            qs = qs.filter(warehouse_code__icontains=warehouse_code)
            
        items, total, page, page_size = paginate_qs(qs, request)
        fields = ['product_sku', 'warehouse_code', 'location_code', 'quantity_before', 'quantity_after', 'diff_qty', 'reason', 'created_at']
        return resp_ok({
            'list': [model_to_dict(i, fields) for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size
        })
    
    if request.method == 'POST':
        # Stocktaking logic: Compare and Adjust
        body = json_body(request)
        product_sku = body.get('product_sku')
        warehouse_code = body.get('warehouse_code')
        location_code = body.get('location_code')
        actual_qty = body.get('actual_qty')
        reason = body.get('reason', '')
        
        if not all([product_sku, warehouse_code, location_code]) or actual_qty is None:
            return resp_err('缺少必要参数')
            
        try:
            # Need to find the exact item by location
            # Note: location_code is now mandatory for precise stocktaking
            item = InventoryItem.objects.get(
                product_sku=product_sku, 
                warehouse_code=warehouse_code,
                location_code=location_code
            )
            
            # Validation: Cannot set quantity lower than locked quantity
            if int(actual_qty) < item.locked_qty:
                return resp_err(f'实盘数量不能小于锁定库存 ({item.locked_qty})，请先处理相关单据')
            
            # Validation: Max capacity check
            if int(actual_qty) > LOCATION_MAX_QTY:
                return resp_err(f'实盘数量 ({actual_qty}) 超过库位容量上限 ({LOCATION_MAX_QTY})')
                
            old_qty = item.quantity
            diff = int(actual_qty) - old_qty
            
            # Save stocktaking record
            InventoryStocktaking.objects.create(
                product_sku=product_sku,
                warehouse_code=warehouse_code,
                location_code=location_code,
                quantity_before=old_qty,
                quantity_after=actual_qty,
                diff_qty=diff,
                reason=reason
            )
            
            if diff != 0:
                item.quantity = actual_qty
                item.save()
                SystemLog.objects.create(
                    operator=user['username'],
                    action='库存盘点',
                    detail=f'盘点调整：{product_sku} @ {warehouse_code}/{location_code}, 原库存 {old_qty} -> 实盘 {actual_qty}, 差异 {diff}, 原因: {reason}'
                )
            return resp_ok({'diff': diff})
            
        except InventoryItem.DoesNotExist:
            # If item doesn't exist but we found it in stocktaking, create it
            # Validation: Max capacity check for new item
            if int(actual_qty) > LOCATION_MAX_QTY:
                return resp_err(f'实盘数量 ({actual_qty}) 超过库位容量上限 ({LOCATION_MAX_QTY})')

            InventoryItem.objects.create(
                product_sku=product_sku,
                warehouse_code=warehouse_code,
                location_code=location_code,
                quantity=actual_qty
            )
            
            InventoryStocktaking.objects.create(
                product_sku=product_sku,
                warehouse_code=warehouse_code,
                location_code=location_code,
                quantity_before=0,
                quantity_after=actual_qty,
                diff_qty=actual_qty,
                reason=reason
            )
            
            SystemLog.objects.create(
                operator=user['username'],
                action='库存盘点',
                detail=f'盘点新增：{product_sku} @ {warehouse_code}/{location_code}, 实盘 {actual_qty}, 原因: {reason}'
            )
            return resp_ok({'diff': actual_qty})
        except Exception as e:
             # Catch unexpected errors like MultipleObjectsReturned if data is dirty
             return resp_err(f'盘点失败: {str(e)}')

    return resp_err('仅支持POST提交盘点结果')


@csrf_exempt
def inventory_transfer(request):
    user, err = require_auth(request)
    if err:
        return err
        
    if request.method == 'GET':
        # List logic - return inventory items with available qty
        # This matches the frontend expectation for the transfer list view
        qs = InventoryItem.objects.all().order_by('-id')
        
        product_sku = request.GET.get('product_sku')
        warehouse_code = request.GET.get('warehouse_code')
        
        if product_sku:
            qs = qs.filter(product_sku__icontains=product_sku)
        if warehouse_code:
            qs = qs.filter(warehouse_code__icontains=warehouse_code)
            
        items, total, page, page_size = paginate_qs(qs, request)
        
        result_list = []
        for i in items:
            d = model_to_dict(i, ['product_sku', 'warehouse_code', 'location_code', 'quantity', 'locked_qty', 'batch_no'])
            d['available_qty'] = i.quantity - i.locked_qty
            result_list.append(d)
            
        return resp_ok({
            'list': result_list,
            'total': total,
            'page': page,
            'pageSize': page_size
        })
        
    if request.method == 'POST':
        body = json_body(request)
        product_sku = body.get('product_sku')
        from_wh = body.get('from_wh')
        from_location = body.get('from_location')
        to_wh = body.get('to_wh')
        to_location = body.get('to_location')
        qty = int(body.get('quantity', 0))
        
        if qty <= 0:
             return resp_err('调拨数量必须大于0')
             
        if not all([product_sku, from_wh, to_wh]):
             return resp_err('缺少必要参数')
             
        with transaction.atomic():
            # Deduct from source (Specific location)
            if from_location:
                try:
                    source_item = InventoryItem.objects.get(
                        product_sku=product_sku, 
                        warehouse_code=from_wh,
                        location_code=from_location
                    )
                    available = source_item.quantity - source_item.locked_qty
                    if available < qty:
                        return resp_err(f'源库位可用库存不足 (可用: {available})')
                    
                    source_item.quantity -= qty
                    source_item.save()
                except InventoryItem.DoesNotExist:
                    return resp_err('源库存记录不存在')
            else:
                # Legacy logic: Deduct from warehouse generally (if no location specified)
                # But frontend now sends location, so this might be fallback
                source_items = InventoryItem.objects.filter(product_sku=product_sku, warehouse_code=from_wh).order_by('location_code', 'id')
                remaining = qty
                for item in source_items:
                    if remaining <= 0: break
                    available = item.quantity - item.locked_qty
                    if available > 0:
                        deduct = min(available, remaining)
                        item.quantity -= deduct
                        item.save()
                        remaining -= deduct
                
                if remaining > 0:
                    return resp_err('调出仓库可用库存不足')
                
            # Add to destination
            # Validate max capacity for destination
            dest_loc = to_location or '调拨入库区'
            
            # Check destination capacity if it exists
            try:
                dest_item = InventoryItem.objects.get(
                    product_sku=product_sku,
                    warehouse_code=to_wh,
                    location_code=dest_loc
                )
                if dest_item.quantity + qty > LOCATION_MAX_QTY:
                     return resp_err(f'目标库位容量不足 (当前: {dest_item.quantity}, 上限: {LOCATION_MAX_QTY})')
                
                dest_item.quantity += qty
                dest_item.save()
            except InventoryItem.DoesNotExist:
                # New item check
                if qty > LOCATION_MAX_QTY:
                    return resp_err(f'调拨数量超过目标库位容量上限 ({LOCATION_MAX_QTY})')
                    
                InventoryItem.objects.create(
                    product_sku=product_sku,
                    warehouse_code=to_wh,
                    location_code=dest_loc,
                    quantity=qty,
                    locked_qty=0
                )
            
            # Record transfer history
            InventoryTransfer.objects.create(
                product_sku=product_sku,
                from_warehouse=from_wh,
                to_warehouse=to_wh,
                qty=qty
            )
            
            SystemLog.objects.create(
                operator=user['username'],
                action='库存调拨',
                detail=f'调拨 {product_sku} {qty} 从 {from_wh}/{from_location} 到 {to_wh}/{dest_loc}'
            )
            
        return resp_ok()

    return resp_err('仅支持POST提交调拨请求')


from django.utils import timezone
from django.db.models import Sum, Count
import datetime

def reports_dashboard(request):
    user, err = require_auth(request)
    if err:
        return err
    
    today = timezone.localdate()
    start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    end_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
    
    # KPI Logic
    # 1. Inbound today
    inbound_today = InboundOrderItem.objects.filter(
        order__created_at__range=(start_of_day, end_of_day)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # 2. Outbound today
    outbound_today = OutboundOrderItem.objects.filter(
        order__created_at__range=(start_of_day, end_of_day)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # 3. Inventory Amount (Total quantity)
    inventory_amount = InventoryItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # 4. SKU Count (Total active products)
    sku_count = Product.objects.filter(is_active=True).count()
    
    # Trend 7d (Real data)
    trend_7d = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        start = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))
        
        in_count = InboundOrderItem.objects.filter(
            order__created_at__range=(start, end)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        out_count = OutboundOrderItem.objects.filter(
            order__created_at__range=(start, end)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        trend_7d.append({
            'date': date.isoformat(),
            'inbound': in_count,
            'outbound': out_count
        })
        
    # Top 10 Products (by inventory quantity)
    top_items = InventoryItem.objects.values('product_sku').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:10]
    top10 = []
    
    # 仅查询需要的两个字段
    products = dict(Product.objects.values_list('sku_code', 'spu_name'))

    for item in top_items:
        sku = item['product_sku']
        top10.append({
            'name': products.get(sku, sku), # Fallback to SKU if name not found
            'qty': item['total_qty']
        })

    data = {
        'kpi': {
            'inbound_today': inbound_today,
            'outbound_today': outbound_today,
            'inventory_amount': inventory_amount,
            'sku_count': sku_count, # Replaced 'order_rate' with something real
        },
        'trend_7d': trend_7d,
        'top10': top10,
    }
    return resp_ok(data)


def reports_daily(request):
    user, err = require_auth(request)
    if err:
        return err
        
    # Generate report for last 30 days
    today = timezone.localdate()
    report_list = []
    
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        start = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))
        
        # Calculate daily item quantity
        # Inbound: based on InboundOrderItem created_at (approx) or order created_at
        # Using InboundOrderItem directly might be better if they track creation time, 
        # but our model InboundOrderItem doesn't have created_at, only InboundOrder has.
        # So we filter orders by date, then sum their items.
        
        in_qty = InboundOrderItem.objects.filter(
            order__created_at__range=(start, end)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        out_qty = OutboundOrderItem.objects.filter(
            order__created_at__range=(start, end)
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Only show days with activity? Or all days? 
        # Usually all days or days with data. Let's show days with data to keep list clean, 
        # or all days if user wants continuity. Let's show all for now but maybe frontend paginates?
        # Frontend has no pagination in ReportsDailyView, just a table.
        # So maybe just return recent 30 days.
        
        report_list.append({
            'date': date.isoformat(),
            'inbound': in_qty,
            'outbound': out_qty
        })
            
    return resp_ok({'list': report_list, 'total': len(report_list)})


@csrf_exempt
def system_users(request):
    return crud_model(request, SystemUser, ['username', 'role', 'name', 'avatar'], search_fields=['username', 'name', 'role'])


@csrf_exempt
def system_roles(request):
    return crud_model(request, SystemRole, ['name'], search_fields=['name'])


@csrf_exempt
def system_logs(request):
    user, err = require_auth(request)
    if err:
        return err
        
    if request.method == 'GET':
        qs = SystemLog.objects.all().order_by('-id')
        detail = request.GET.get('detail')
        action = request.GET.get('action')
        operator = request.GET.get('operator')
        
        if detail:
            qs = qs.filter(detail__icontains=detail)
        if action:
            qs = qs.filter(action__icontains=action)
        if operator:
            qs = qs.filter(operator__icontains=operator)
            
        items, total, page, page_size = paginate_qs(qs, request)
        fields = ['id', 'operator', 'action', 'detail', 'created_at']
        return resp_ok({
            'list': [model_to_dict(i, fields) for i in items],
            'total': total,
            'page': page,
            'pageSize': page_size,
        })
        
    return resp_err('方法不允许', 405)
