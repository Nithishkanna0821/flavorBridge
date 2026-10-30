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
        if not user_id or not User.query.get(user_id):
            session.clear()
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

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
                session.clear()
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', role=required_role, next=request.path))

            if user.role != required_role:
                flash(f'Access restricted. This section is for {required_role.replace("_", " ")}s only.', 'danger')
                if user.role == 'food_maker':
                    return redirect(url_for('food_maker.dashboard'))
                return redirect(url_for('auth.customer_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
