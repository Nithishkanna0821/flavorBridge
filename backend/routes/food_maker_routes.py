import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from backend.extensions import db
from backend.models import FoodMaker, User, Product, Order, OrderItem, Review
from backend.utils.security import login_required, role_required, get_or_create_food_maker
from backend.utils.validators import save_uploaded_image

food_maker_bp = Blueprint('food_maker', __name__)

@food_maker_bp.route('/food-makers')
def food_makers_list():
    city_filter = request.args.get('city', '').strip()
    cuisine_filter = request.args.get('cuisine', '').strip()
    verified_only = request.args.get('verified') in ['1', 'true', 'True']

    query = FoodMaker.query

    if verified_only:
        query = query.filter(FoodMaker.is_verified == True)

    makers = query.all()

    if city_filter:
        makers = [m for m in makers if m.user and city_filter.lower() in (m.user.city or '').lower()]

    if cuisine_filter:
        makers = [m for m in makers if cuisine_filter.lower() in (m.cuisines or '').lower() or cuisine_filter.lower() in (m.speciality or '').lower()]

    all_cities = sorted(list(set(m.user.city for m in FoodMaker.query.all() if m.user and m.user.city)))

    return render_template(
        'food_makers.html',
        makers=makers,
        cities=all_cities,
        selected_city=city_filter,
        selected_cuisine=cuisine_filter,
        verified_only=verified_only
    )


@food_maker_bp.route('/food-maker/<int:maker_id>')
def food_maker_profile(maker_id):
    maker = FoodMaker.query.get_or_404(maker_id)
    products = Product.query.filter_by(food_maker_id=maker.id).order_by(Product.created_at.desc()).all()
    reviews = Review.query.filter_by(food_maker_id=maker.id).order_by(Review.created_at.desc()).all()
    return render_template(
        'food_maker_profile.html',
        maker=maker,
        products=products,
        reviews=reviews
    )


@food_maker_bp.route('/food-maker/dashboard')
@login_required
@role_required('food_maker')
def dashboard():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    if not maker:
        return redirect(url_for('auth.login'))

    # Recalculate verification score to keep it fresh
    maker.calculate_verification_score()
    db.session.commit()

    products = Product.query.filter_by(food_maker_id=maker.id).all()
    product_ids = [p.id for p in products]

    # Find all orders containing this maker's items
    order_items = OrderItem.query.filter(OrderItem.food_maker_id == maker.id).all()
    order_ids = list(set(item.order_id for item in order_items))
    orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all() if order_ids else []

    pending_orders = [o for o in orders if o.status in ['Pending', 'Accepted', 'Preparing', 'Shipped', 'Out for Delivery']]
    completed_orders = [o for o in orders if o.status == 'Delivered']

    total_revenue = sum(item.subtotal for item in order_items if item.order and item.order.status != 'Cancelled')

    return render_template(
        'food_maker_dashboard.html',
        maker=maker,
        products=products,
        orders=orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        total_revenue=total_revenue
    )


from datetime import datetime
from backend.models import DailyVerification

@food_maker_bp.route('/verification', methods=['GET', 'POST'])
@login_required
@role_required('food_maker')
def verification():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    if not maker:
        return redirect(url_for('auth.login'))
    user = maker.user

    if request.method == 'POST':
        user.name = request.form.get('name', user.name).strip()
        user.phone = request.form.get('phone', user.phone).strip()
        user.city = request.form.get('city', user.city).strip()
        user.address = request.form.get('address', user.address).strip()

        maker.speciality = request.form.get('speciality', maker.speciality).strip()
        maker.cuisines = request.form.get('cuisines', maker.cuisines).strip()
        maker.description = request.form.get('description', maker.description).strip()

        try:
            maker.years_experience = int(request.form.get('years_experience', maker.years_experience))
        except ValueError:
            pass

        # Handle profile image upload
        image_file = request.files.get('profile_image')
        if image_file and image_file.filename:
            upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads'))
            new_img = save_uploaded_image(image_file, upload_dir)
            if new_img:
                maker.profile_image = new_img

        score = maker.calculate_verification_score()
        db.session.commit()

        if maker.is_verified:
            flash(f'🎉 Congratulations! Your score is {score}/100. You are now a Verified Food Maker!', 'success')
        else:
            flash(f'Verification details updated. Current score: {score}/100. Need 80+ for Verified badge.', 'info')

        return redirect(url_for('food_maker.verification_status'))

    maker.calculate_verification_score()
    today_log = maker.today_verification
    past_logs = DailyVerification.query.filter_by(food_maker_id=maker.id).order_by(DailyVerification.created_at.desc()).limit(10).all()
    today_date_str = datetime.utcnow().strftime('%B %d, %Y')
    
    return render_template(
        'verification.html',
        maker=maker,
        user=user,
        today_log=today_log,
        past_logs=past_logs,
        today_date_str=today_date_str
    )


@food_maker_bp.route('/verification/daily-upload', methods=['POST'])
@login_required
@role_required('food_maker')
def daily_verification_upload():
    """Uploads today's ingredients log and photo of the freshly prepared final dish."""
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)

    ingredients_used = request.form.get('ingredients_used', '').strip()
    dishes_prepared = request.form.get('dishes_prepared', '').strip()
    sourcing_notes = request.form.get('sourcing_notes', '').strip()

    if not ingredients_used:
        flash('Please specify the ingredients used for today\'s fresh batch.', 'danger')
        return redirect(url_for('food_maker.verification'))

    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    existing_log = DailyVerification.query.filter_by(food_maker_id=maker.id, log_date=today_str).first()

    image_file = request.files.get('dish_image')
    image_filename = existing_log.dish_image if existing_log else ''

    if image_file and image_file.filename:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads'))
        new_img = save_uploaded_image(image_file, upload_dir)
        if new_img:
            image_filename = new_img

    if not existing_log and not image_filename:
        flash('Please upload a photo of today\'s freshly prepared final dish or fresh ingredients setup.', 'warning')
        return redirect(url_for('food_maker.verification'))

    if existing_log:
        existing_log.ingredients_used = ingredients_used
        existing_log.dishes_prepared = dishes_prepared
        existing_log.sourcing_notes = sourcing_notes
        if image_filename:
            existing_log.dish_image = image_filename
        existing_log.created_at = datetime.utcnow()
    else:
        daily_entry = DailyVerification(
            food_maker_id=maker.id,
            log_date=today_str,
            ingredients_used=ingredients_used,
            dishes_prepared=dishes_prepared,
            dish_image=image_filename,
            sourcing_notes=sourcing_notes
        )
        db.session.add(daily_entry)

    # Recalculate maker score
    maker.calculate_verification_score()
    db.session.commit()

    flash(f'✨ Today\'s fresh ingredients & final dish photo verified successfully! Your profile now displays the Fresh Batch Verified Today badge.', 'success')
    return redirect(url_for('food_maker.verification'))


@food_maker_bp.route('/verification/status')
@login_required
@role_required('food_maker')
def verification_status():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    if not maker:
        return redirect(url_for('auth.login'))
    maker.calculate_verification_score()
    db.session.commit()
    today_log = maker.today_verification
    return render_template('verification_status.html', maker=maker, today_log=today_log)


@food_maker_bp.route('/food-maker/orders')
@login_required
@role_required('food_maker')
def food_maker_orders():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    if not maker:
        return redirect(url_for('auth.login'))

    # Find all orders containing this maker's items
    order_items = OrderItem.query.filter(OrderItem.food_maker_id == maker.id).all()
    order_ids = list(set(item.order_id for item in order_items))
    orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all() if order_ids else []

    status_filter = request.args.get('status', '').strip()
    if status_filter:
        orders = [o for o in orders if o.status == status_filter]

    return render_template('maker_orders.html', maker=maker, orders=orders, selected_status=status_filter)
