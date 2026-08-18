from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    sku_code = models.CharField(max_length=50, unique=True)
    spu_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=10, blank=True, null=True)
    safety_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    barcode = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    rating = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    credit_limit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InboundOrder(models.Model):
    order_no = models.CharField(max_length=50, unique=True)
    supplier_name = models.CharField(max_length=100, blank=True, null=True)
    warehouse_code = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, default='草稿')
    planned_date = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    reject_reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InboundOrderItem(models.Model):
    order = models.ForeignKey(InboundOrder, related_name='items', on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    received_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    putaway_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    location_code = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, default='草稿')
    reason = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['product_sku']),
        ]


class OutboundOrder(models.Model):
    order_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    warehouse_code = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, default='草稿')
    planned_date = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    reject_reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OutboundOrderItem(models.Model):
    order = models.ForeignKey(OutboundOrder, related_name='items', on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        indexes = [
            models.Index(fields=['product_sku']),
        ]


class InventoryItem(models.Model):
    product_sku = models.CharField(max_length=50)
    warehouse_code = models.CharField(max_length=50, blank=True, null=True)
    location_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    locked_qty = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    batch_no = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['product_sku', 'warehouse_code']),
            models.Index(fields=['product_sku', 'warehouse_code', 'location_code']),
        ]


class InventoryStocktaking(models.Model):
    warehouse_code = models.CharField(max_length=50)
    product_sku = models.CharField(max_length=50)
    location_code = models.CharField(max_length=50, blank=True, null=True)
    quantity_before = models.IntegerField(default=0)
    quantity_after = models.IntegerField(default=0)
    diff_qty = models.IntegerField(default=0)
    reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InventoryTransfer(models.Model):
    product_sku = models.CharField(max_length=50)
    from_warehouse = models.CharField(max_length=50)
    to_warehouse = models.CharField(max_length=50)
    qty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class SystemRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SystemUser(models.Model):
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SystemLog(models.Model):
    operator = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
