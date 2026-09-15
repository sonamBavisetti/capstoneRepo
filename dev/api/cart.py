from flask import Blueprint, jsonify, request

cart_bp = Blueprint('cart', __name__)

# Minimal in-memory demo cart per-session is out-of-scope; provide simple endpoints
CARTS = {}

@cart_bp.route('/api/cart/<customer_id>', methods=['GET'])
def get_cart(customer_id):
    return jsonify(CARTS.get(customer_id, {}))

@cart_bp.route('/api/cart/<customer_id>/add', methods=['POST'])
def add_to_cart(customer_id):
    data = request.json or {}
    item = data.get('item')
    if not item:
        return jsonify({'error': 'missing item'}), 400
    CARTS.setdefault(customer_id, {}).setdefault('items', []).append(item)
    return jsonify({'status': 'ok', 'cart': CARTS[customer_id]})
