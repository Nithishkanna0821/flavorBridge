from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.extensions import db
from backend.models import User, Cart, CartItem, Product, Interaction

cart_bp = Blueprint('cart', __name__)

def get_current_user_id() -> int:
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if not user and session.get('user_email'):
        user = User.query.filter_by(email=session.get('user_email')).first()
    if not user:
        user_role = session.get('user_role', 'customer')
        user = User.query.filter_by(role=user_role).first()
    if not user:
        user = User.query.first()
    if user:
        session.permanent = True
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name
        session['user_email'] = user.email
        return user.id
    return 1

def get_or_create_cart(user_id: int) -> Cart:
    """Helper to fetch or create a user's persistent cart."""
    cart = Cart.query.filter_by(customer_id=user_id).first()
    if not cart:
        cart = Cart(customer_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

@cart_bp.route('/cart')
def view_cart():
    user_id = get_current_user_id()
    cart = get_or_create_cart(user_id)
    
    subtotal = cart.total_amount
    delivery_fee = 0.0 if subtotal >= 499 or subtotal == 0 else 40.0
    total = subtotal + delivery_fee
    
    return render_template(
        'cart.html',
        cart=cart,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total
    )

@cart_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    user_id = get_current_user_id()
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        reset_cart = bool(data.get('reset_cart', False))
    else:
        product_id = request.form.get('product_id', type=int)
        quantity = int(request.form.get('quantity', 1))
        reset_cart = bool(request.form.get('reset_cart', False))

    if not product_id or quantity <= 0:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid product or quantity.'}), 400
        flash('Invalid product or quantity.', 'danger')
        return redirect(request.referrer or url_for('product.products_list'))

    product = Product.query.get_or_404(product_id)
    
    if product.stock <= 0:
        if request.is_json:
            return jsonify({'success': False, 'message': 'This regional delicacy is currently out of stock.'}), 400
        flash('This item is currently out of stock.', 'warning')
        return redirect(request.referrer or url_for('product.products_list'))

    cart = get_or_create_cart(user_id)

    # Enforce Single Kitchen Rule (One customer can order products from only one kitchen per order)
    existing_maker = cart.food_maker
    if existing_maker and existing_maker.id != product.food_maker_id:
        existing_maker_name = existing_maker.user.name if (existing_maker.user and existing_maker.user.name) else f"Kitchen #{existing_maker.id}"
        new_maker_name = product.food_maker.user.name if (product.food_maker and product.food_maker.user and product.food_maker.user.name) else "this kitchen"
        
        if not reset_cart:
            conflict_msg = (
                f'Your cart already contains delicacies from "{existing_maker_name}". '
                f'Each order can only be prepared and dispatched from one kitchen at a time. '
                f'Would you like to clear your cart and start a fresh order from "{new_maker_name}"?'
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'conflict': True,
                    'existing_kitchen': existing_maker_name,
                    'new_kitchen': new_maker_name,
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'message': conflict_msg
                }), 409
            
            flash(conflict_msg, 'warning')
            return redirect(url_for('cart.view_cart'))
        else:
            # User chose to reset cart and switch kitchen
            for old_item in list(cart.items):
                db.session.delete(old_item)
            db.session.flush()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    # Log CART interaction for AI engine
    interaction = Interaction(customer_id=user_id, product_id=product.id, interaction_type='CART')
    db.session.add(interaction)

    db.session.commit()

    maker_name = product.food_maker.user.name if product.food_maker and product.food_maker.user else "Kitchen"

    if request.is_json:
        return jsonify({
            'success': True,
            'message': f'"{product.name}" added to your cart from {maker_name}!',
            'cart_count': cart.total_items,
            'cart_total': cart.total_amount,
            'kitchen_name': maker_name
        })

    flash(f'"{product.name}" has been added to your cart!', 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/clear-cart', methods=['POST'])
def clear_cart():
    user_id = get_current_user_id()
    cart = get_or_create_cart(user_id)
    
    for item in list(cart.items):
        db.session.delete(item)
    db.session.commit()

    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update-cart', methods=['POST'])
def update_cart():
    user_id = get_current_user_id()
    cart = get_or_create_cart(user_id)

    if request.is_json:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    else:
        item_id = request.form.get('item_id', type=int)
        quantity = int(request.form.get('quantity', 1))

    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Item not found in your cart.'}), 404
        flash('Item not found in cart.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()

    if request.is_json:
        subtotal = cart.total_amount
        delivery_fee = 0.0 if subtotal >= 499 or subtotal == 0 else 40.0
        return jsonify({
            'success': True,
            'cart_count': cart.total_items,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'total': subtotal + delivery_fee,
            'item_subtotal': cart_item.subtotal if quantity > 0 else 0
        })

    flash('Cart updated successfully.', 'success')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    user_id = get_current_user_id()
    cart = get_or_create_cart(user_id)
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()

    db.session.delete(cart_item)
    db.session.commit()

    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/api/cart-count')
def api_cart_count():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'count': 0, 'total': 0.0})
    cart = Cart.query.filter_by(customer_id=user_id).first()
    if not cart:
        return jsonify({'count': 0, 'total': 0.0})
    return jsonify({'count': cart.total_items, 'total': cart.total_amount})
