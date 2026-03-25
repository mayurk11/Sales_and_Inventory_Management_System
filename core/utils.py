import uuid
from datetime import datetime

def generate_order_number():
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4]}"