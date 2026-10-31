from flask import Blueprint, request, redirect, url_for, flash, session
from backend.extensions import db
from backend.models import Review, Product, FoodMaker
from backend.utils.security import login_required, role_required

review_bp = Blueprint('review', __name__)

@review_bp.route('/add-review', methods=['POST'])
@login_required
def add_review():
    user_id = session.get('user_id')
    product_id = request.form.get('product_id', type=int)
    food_maker_id = request.form.get('food_maker_id', type=int)
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Please select a valid rating between 1 and 5 stars.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # Infer food_maker_id from product if missing
    if not food_maker_id and product_id:
        prod = Product.query.get(product_id)
        if prod:
            food_maker_id = prod.food_maker_id

    if not food_maker_id:
        flash('Invalid food maker or product for review.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # Create new review
    review = Review(
        customer_id=user_id,
        product_id=product_id,
        food_maker_id=food_maker_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()

    flash('⭐ Thank you for your review! Your feedback supports local regional food makers.', 'success')
    return redirect(request.referrer or url_for('product.product_detail', product_id=product_id))
