from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from backend.extensions import db
from backend.models import User, Cart, Order, OrderItem, Product, Interaction, FoodMaker
from backend.utils.security import login_required, role_required, get_or_create_food_maker

order_bp = Blueprint('order', __name__)

@order_bp.route('/checkout')
@login_required
@role_required('customer')
def checkout():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    cart = Cart.query.filter_by(customer_id=user_id).first()

    if not cart or not cart.items:
        flash('Your cart is empty. Please add items to checkout.', 'warning')
        return redirect(url_for('product.products_list'))

    subtotal = cart.total_amount
    delivery_fee = 0.0 if subtotal >= 499 else 40.0
    total = subtotal + delivery_fee

    return render_template(
        'checkout.html',
        user=user,
        cart=cart,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total
    )


@order_bp.route('/place-order', methods=['POST'])
@login_required
@role_required('customer')
def place_order():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    cart = Cart.query.filter_by(customer_id=user_id).first()

    if not cart or not cart.items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('product.products_list'))

    address = request.form.get('address', user.address).strip()
    city = request.form.get('city', user.city).strip()
    state = request.form.get('state', 'Tamil Nadu').strip()
    pincode = request.form.get('pincode', '').strip()
    phone = request.form.get('phone', user.phone).strip()
    payment_method = request.form.get('payment_method', 'Cash on Delivery').strip()

    if not address or not city or not pincode or not phone:
        flash('Please fill in complete delivery address and contact details.', 'danger')
        return redirect(url_for('order.checkout'))

    # Validate that all items in cart belong to a single kitchen
    maker_ids = {item.product.food_maker_id for item in cart.items if item.product}
    if len(maker_ids) > 1:
        flash('Each order can only contain products from a single kitchen. Please update your cart.', 'warning')
        return redirect(url_for('cart.view_cart'))

    subtotal = cart.total_amount
    delivery_fee = 0.0 if subtotal >= 499 else 40.0
    total_amount = subtotal + delivery_fee

    # Create Order
    order = Order(
        customer_id=user.id,
        total_amount=total_amount,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        phone=phone,
        payment_method=payment_method,
        status='Pending'
    )
    db.session.add(order)
    db.session.flush()

    # Create Order Items and log PURCHASE interactions
    for item in cart.items:
        prod = item.product
        if not prod:
            continue

        order_item = OrderItem(
            order_id=order.id,
            product_id=prod.id,
            food_maker_id=prod.food_maker_id,
            quantity=item.quantity,
            price=prod.price
        )
        db.session.add(order_item)

        # Reduce stock
        if prod.stock >= item.quantity:
            prod.stock -= item.quantity
        else:
            prod.stock = 0

        # AI PURCHASE interaction
        purchase_interaction = Interaction(
            customer_id=user.id,
            product_id=prod.id,
            interaction_type='PURCHASE'
        )
        db.session.add(purchase_interaction)

    # Empty customer cart
    for item in list(cart.items):
        db.session.delete(item)

    db.session.commit()

    flash('🎉 Your order has been placed successfully with Cash on Delivery!', 'success')
    return redirect(url_for('order.order_confirmation', order_id=order.id))


@order_bp.route('/order-confirmation/<int:order_id>')
@login_required
@role_required('customer')
def order_confirmation(order_id):
    user_id = session.get('user_id')
    order = Order.query.filter_by(id=order_id, customer_id=user_id).first_or_404()
    return render_template('order_confirmation.html', order=order)


@order_bp.route('/orders')
@login_required
@role_required('customer')
def customer_orders():
    user_id = session.get('user_id')
    orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)


@order_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    order = Order.query.get_or_404(order_id)

    # Authorization: customer can view their own order; food maker can view order containing their items
    if user_role == 'customer':
        if order.customer_id != user_id:
            abort(403)
    elif user_role == 'food_maker':
        maker = FoodMaker.query.filter_by(user_id=user_id).first()
        if not maker or not any(item.food_maker_id == maker.id for item in order.items):
            abort(403)

    # Collect unique food makers associated with the items in this order
    unique_makers = []
    seen_maker_ids = set()
    for item in order.items:
        if item.food_maker and item.food_maker.id not in seen_maker_ids:
            seen_maker_ids.add(item.food_maker.id)
            unique_makers.append(item.food_maker)

    return render_template(
        'order_detail.html',
        order=order,
        user_role=user_role,
        unique_makers=unique_makers
    )


@order_bp.route('/update-order-status', methods=['POST'])
@login_required
@role_required('food_maker')
def update_order_status():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)

    order_id = request.form.get('order_id', type=int)
    new_status = request.form.get('status', '').strip()

    order = Order.query.get_or_404(order_id)

    # Verify that this order contains products from this maker
    maker_items = [item for item in order.items if item.food_maker_id == maker.id]
    if not maker_items:
        flash('You are not authorized to update this order.', 'danger')
        return redirect(url_for('food_maker.dashboard'))

    valid_statuses = ['Pending', 'Accepted', 'Preparing', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled']
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to "{new_status}".', 'success')
    else:
        flash('Invalid status selected.', 'danger')

    return redirect(request.referrer or url_for('food_maker.dashboard'))
