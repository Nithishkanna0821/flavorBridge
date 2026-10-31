from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User

def hash_password(password: str) -> str:
    """Hash a plaintext password using Werkzeug."""
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verify a plaintext password against the stored hash."""
    return check_password_hash(password_hash, password)

def get_current_user():
    """Retrieve the currently authenticated User instance, or None."""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return None
        return user
    return None

def login_required(f):
    """Decorator to enforce that the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        user = User.query.get(user_id)
        if not user:
            user_email = session.get('user_email')
            if user_email:
                user = User.query.filter_by(email=user_email).first()
                if user:
                    session['user_id'] = user.id
        if not user:
            session.clear()
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def get_or_create_food_maker(user_id):
    """Ensure a FoodMaker profile exists for this user, creating one if needed."""
    from backend.extensions import db
    from backend.models import FoodMaker
    user = User.query.get(user_id)
    if not user:
        return None
    maker = FoodMaker.query.filter_by(user_id=user.id).first()
    if not maker:
        maker = FoodMaker(
            user_id=user.id,
            speciality='Authentic Traditional Kitchen',
            years_experience=3,
            cuisines='Regional Traditional Cuisine',
            is_verified=True,
            verification_status='Verified',
            description=f"Welcome to {user.name}'s artisanal regional kitchen on FlavorBridge. Handcrafting authentic heritage recipes with natural spices and pure ingredients."
        )
        maker.calculate_verification_score()
        db.session.add(maker)
        db.session.commit()
    return maker

def role_required(required_role):
    """Decorator to enforce that the logged-in user has a specific role ('customer' or 'food_maker')."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', role=required_role, next=request.path))
            
            user = User.query.get(user_id)
            if not user:
                user_email = session.get('user_email')
                if user_email:
                    user = User.query.filter_by(email=user_email).first()
                    if user:
                        session['user_id'] = user.id
            if not user:
                session.clear()
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', role=required_role, next=request.path))

            if user.role != required_role:
                from backend.extensions import db
                if required_role == 'food_maker' and (user.food_maker_profile or session.get('user_role') == 'food_maker'):
                    user.role = 'food_maker'
                    db.session.commit()
                    return f(*args, **kwargs)

                flash(f'Access restricted. This section is for {required_role.replace("_", " ")}s only.', 'danger')
                if user.role == 'food_maker':
                    return redirect(url_for('food_maker.dashboard'))
                else:
                    return redirect(url_for('auth.customer_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
