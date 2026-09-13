from typing import Any, Dict


def validate_order_payload(payload: Dict[str, Any]) -> None:
    if 'items' not in payload or not isinstance(payload['items'], list) or len(payload['items']) == 0:
        raise ValueError('order must contain items')
    if 'customer' not in payload or 'email' not in payload['customer']:
        raise ValueError('customer.email required')

    for item in payload['items']:
        if not item.get('product_id'):
            raise ValueError('each item requires product_id')
        qty = item.get('quantity', 1)
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError('quantity must be a positive integer')
