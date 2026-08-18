import os
import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from api.models import InboundOrder

def inspect_order(order_no):
    print(f"--- Inspecting Order: {order_no} ---")
    try:
        order = InboundOrder.objects.get(order_no=order_no)
        print(f"Order Found: {order.order_no}")
        print(f"Created At (Raw DB value): {order.created_at}")
        print(f"Created At (Local Time): {timezone.localtime(order.created_at)}")
        print(f"Created At Date (Local): {timezone.localtime(order.created_at).date()}")
        
        # Check Today
        today = timezone.localdate()
        print(f"--- System Today ---")
        print(f"Timezone.now(): {timezone.now()}")
        print(f"Timezone.localdate(): {today}")
        
        # Check Query Match
        count = InboundOrder.objects.filter(created_at__date=today).count()
        print(f"--- Query Result ---")
        print(f"Count for today ({today}): {count}")
        
        # Check if this specific order matches
        matches = InboundOrder.objects.filter(created_at__date=today, order_no=order_no).exists()
        print(f"Does this order match 'created_at__date=today'? {matches}")
        
        if not matches:
            # Debug why
            order_local_date = timezone.localtime(order.created_at).date()
            print(f"Mismatch Details:")
            print(f"  Order Local Date: {order_local_date}")
            print(f"  Query Date: {today}")
            print(f"  Are they equal? {order_local_date == today}")

    except InboundOrder.DoesNotExist:
        print(f"Order {order_no} not found in DB.")

if __name__ == "__main__":
    inspect_order('IN-20260304-708')
