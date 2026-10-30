import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort, jsonify
from backend.extensions import db
from backend.models import Product, FoodMaker, User, Review, Interaction
from backend.utils.security import login_required, role_required, get_or_create_food_maker
from backend.utils.validators import validate_product_data, save_uploaded_image
from backend.ai.smart_search import search_products
from backend.ai.recommender import get_similar_products

product_bp = Blueprint('product', __name__)

FOOD_CATEGORIES = [
    "Spice Powders & Seasonings",
    "Traditional Snacks",
    "Traditional Sweets",
    "Pickles",
    "Beverages",
    "Homemade Food Products",
    "Fresh Regional Foods"
]

@product_bp.route('/products')
def products_list():
    query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()
    selected_city = request.args.get('city', '').strip()
    selected_type = request.args.get('product_type', '').strip()
    verified_only = request.args.get('verified_only') in ['1', 'true', 'True', 'yes']
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    sort_by = request.args.get('sort', 'newest')

    # Start with all products
    base_query = Product.query

    # Apply category filter
    if selected_category:
        base_query = base_query.filter(Product.category == selected_category)

    # Apply city filter
    if selected_city:
        base_query = base_query.filter(Product.city.ilike(f"%{selected_city}%"))

    # Apply product type filter
    if selected_type in ['Packaged Food', 'Fresh Food']:
        base_query = base_query.filter(Product.product_type == selected_type)

    # Apply price range filters
    if min_price is not None:
        base_query = base_query.filter(Product.price >= min_price)
    if max_price is not None:
        base_query = base_query.filter(Product.price <= max_price)

    # Apply verified maker filter
    if verified_only:
        base_query = base_query.join(FoodMaker).filter(FoodMaker.is_verified == True)

    candidate_products = base_query.all()

    # Apply Smart TF-IDF Search if query is present
    if query:
        ranked_scored = search_products(query, candidate_products)
        products = [p for p, score in ranked_scored]
    else:
        products = candidate_products

    # Apply rating filter (calculated property)
    if min_rating:
        products = [p for p in products if p.average_rating >= min_rating]

    # Sorting
    if sort_by == 'price_asc':
        products = sorted(products, key=lambda p: p.price)
    elif sort_by == 'price_desc':
        products = sorted(products, key=lambda p: p.price, reverse=True)
    elif sort_by == 'rating':
        products = sorted(products, key=lambda p: (p.average_rating, p.rating_count), reverse=True)
    elif sort_by == 'popular':
        products = sorted(products, key=lambda p: (p.rating_count, p.average_rating), reverse=True)
    else:
        # Default 'newest' / catalog browse: Newly added handcrafted regional delicacies first!
        products = sorted(products, key=lambda p: (p.created_at or datetime.min), reverse=True)

    # Get distinct cities for filter dropdown
    all_cities = sorted(list(set(p.city for p in Product.query.all() if p.city)))

    return render_template(
        'products.html',
        products=products,
        categories=FOOD_CATEGORIES,
        cities=all_cities,
        query=query,
        selected_category=selected_category,
        selected_city=selected_city,
        selected_type=selected_type,
        verified_only=verified_only,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        total_count=len(products)
    )


@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    maker = product.food_maker

    # Log user VIEW interaction for AI recommendations
    user_id = session.get('user_id')
    if user_id:
        # Avoid flood logging duplicate views within same session
        interaction = Interaction(customer_id=user_id, product_id=product.id, interaction_type='VIEW')
        db.session.add(interaction)
        db.session.commit()

    # Get AI similar products
    similar_products = get_similar_products(product.id, top_k=4)

    # Get reviews
    reviews = Review.query.filter_by(product_id=product.id).order_by(Review.created_at.desc()).all()

    return render_template(
        'product_detail.html',
        product=product,
        maker=maker,
        similar_products=similar_products,
        reviews=reviews
    )


@product_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    # If visitor is not logged in, redirect them directly to sign in with next target
    if not user:
        flash('Please sign in to your Food Maker partner account to add new dishes.', 'info')
        return redirect(url_for('auth.login', role='food_maker', next=url_for('product.add_product')))

    # Seamlessly activate food maker capabilities for any authenticated user
    if user.role != 'food_maker':
        user.role = 'food_maker'
        session['user_role'] = 'food_maker'
        db.session.commit()

    # Ensure maker kitchen profile exists
    maker = get_or_create_food_maker(user.id)

    if request.method == 'POST':
        is_valid, err_msg = validate_product_data(request.form)
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('add_product.html', categories=FOOD_CATEGORIES, maker=maker)

        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        try:
            price = float(request.form.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0

        try:
            stock = int(request.form.get('stock', 10))
        except (ValueError, TypeError):
            stock = 10

        product_type = request.form.get('product_type', 'Packaged Food').strip()
        preparation_time = request.form.get('preparation_time', '1 day').strip()
        net_quantity = request.form.get('net_quantity', '250g').strip()
        city = request.form.get('city', maker.user.city or 'Chennai').strip()
        region = request.form.get('region', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        description = request.form.get('description', '').strip()

        # Handle image upload safely with Vercel upload directory
        image_file = request.files.get('image')
        image_filename = ''
        if image_file and image_file.filename:
            upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads'))
            image_filename = save_uploaded_image(image_file, upload_dir)

        product = Product(
            food_maker_id=maker.id,
            name=name,
            category=category,
            price=price,
            stock=stock,
            product_type=product_type,
            preparation_time=preparation_time,
            net_quantity=net_quantity,
            city=city,
            region=region,
            ingredients=ingredients,
            description=description,
            image=image_filename
        )
        db.session.add(product)
        db.session.flush()

        # Recalculate maker's verification score
        maker.calculate_verification_score()
        db.session.commit()

        flash(f'Product "{name}" ({net_quantity}) added successfully to your regional kitchen catalog!', 'success')
        return redirect(url_for('product.my_products'))

    return render_template('add_product.html', categories=FOOD_CATEGORIES, maker=maker)


@product_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required('food_maker')
def edit_product(product_id):
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    product = Product.query.get_or_404(product_id)

    if product.food_maker_id != maker.id:
        abort(403)

    if request.method == 'POST':
        is_valid, err_msg = validate_product_data(request.form)
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('edit_product.html', product=product, categories=FOOD_CATEGORIES)

        product.name = request.form.get('name').strip()
        product.category = request.form.get('category').strip()
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock', product.stock))
        product.product_type = request.form.get('product_type', product.product_type).strip()
        product.preparation_time = request.form.get('preparation_time', product.preparation_time).strip()
        product.net_quantity = request.form.get('net_quantity', product.net_quantity or '250g').strip()
        product.city = request.form.get('city', product.city).strip()
        product.region = request.form.get('region', product.region).strip()
        product.ingredients = request.form.get('ingredients', product.ingredients).strip()
        product.description = request.form.get('description', product.description).strip()

        # Handle image upload if a new one was provided
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads'))
            new_image = save_uploaded_image(image_file, upload_dir)
            if new_image:
                product.image = new_image

        maker.calculate_verification_score()
        db.session.commit()

        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('product.my_products'))

    return render_template('edit_product.html', product=product, categories=FOOD_CATEGORIES)


@product_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
@role_required('food_maker')
def delete_product(product_id):
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    product = Product.query.get_or_404(product_id)

    if product.food_maker_id != maker.id:
        abort(403)

    prod_name = product.name
    db.session.delete(product)
    maker.calculate_verification_score()
    db.session.commit()

    flash(f'Product "{prod_name}" has been removed from your store.', 'info')
    return redirect(url_for('product.my_products'))


@product_bp.route('/my-products')
@login_required
@role_required('food_maker')
def my_products():
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id)
    products = Product.query.filter_by(food_maker_id=maker.id).order_by(Product.created_at.desc()).all()
    return render_template('my_products.html', maker=maker, products=products)


@product_bp.route('/api/sync-products', methods=['POST'])
def sync_products():
    """Sync locally cached dishes into the database (guarantees permanence on serverless instances)."""
    user_id = session.get('user_id')
    maker = get_or_create_food_maker(user_id) if user_id else None

    data = request.get_json(silent=True) or {}
    dishes = data.get('dishes', [])

    synced = 0
    if maker and isinstance(dishes, list):
        for d in dishes:
            name = (d.get('name') or '').strip()
            if not name:
                continue
            existing = Product.query.filter_by(food_maker_id=maker.id, name=name).first()
            if not existing:
                try:
                    price = float(d.get('price', 150))
                except (ValueError, TypeError):
                    price = 150.0
                try:
                    stock = int(d.get('stock', 20))
                except (ValueError, TypeError):
                    stock = 20
                prod = Product(
                    food_maker_id=maker.id,
                    name=name,
                    category=d.get('category') or 'Traditional Snacks',
                    price=price,
                    stock=stock,
                    product_type=d.get('product_type') or 'Packaged Food',
                    preparation_time=d.get('preparation_time') or '1 day',
                    net_quantity=d.get('net_quantity') or '250g',
                    city=d.get('city') or (maker.user.city if maker.user else '') or 'Chennai',
                    region=d.get('region') or '',
                    ingredients=d.get('ingredients') or '',
                    description=d.get('description') or '',
                    image=d.get('image') or ''
                )
                db.session.add(prod)
                synced += 1
        if synced > 0:
            maker.calculate_verification_score()
            db.session.commit()

    return jsonify({"status": "ok", "synced": synced})
