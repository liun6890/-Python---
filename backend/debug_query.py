import os
import django
from django.conf import settings
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from api.models import InboundOrder

def debug_query():
    today = timezone.localdate()
    print(f"Today: {today}")
    
    # 1. Range Query (Manual)
    start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    end_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
    
    print(f"Range Start (Aware): {start_of_day}")
    print(f"Range End (Aware): {end_of_day}")
    
    count_range = InboundOrder.objects.filter(created_at__range=(start_of_day, end_of_day)).count()
    print(f"Count (Range): {count_range}")
    
    # 2. Contains Query (String check - just for debug, might be slow)
    # MySQL stores as UTC usually if USE_TZ=True.
    
    # 3. Raw SQL
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT order_no, created_at FROM api_inboundorder ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("Raw DB Rows:")
        for r in rows:
            print(r)

if __name__ == "__main__":
    debug_query()
