from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.extensions import db
from backend.models import User, FoodMaker, Order, Interaction, Product
from backend.utils.security import hash_password, verify_password, login_required, role_required, get_or_create_food_maker
from backend.utils.validators import validate_email, validate_phone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    user_id = session.get('user_id')
    if user_id:
        existing = User.query.get(user_id)
        if not existing:
            session.clear()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'customer').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()

        # Validation
        if not name or not email or not password:
            flash('Name, email, and password are required.', 'danger')
            return render_template('register.html', role=role)

        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', role=role)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', role=role)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role if role in ['customer', 'food_maker'] else 'customer',
            phone=phone,
            city=city,
            address=address
        )
        db.session.add(user)
        db.session.flush()

        # If food maker, create maker profile
        if role == 'food_maker':
            speciality = request.form.get('speciality', '').strip()
            years_experience = request.form.get('years_experience', '0').strip()
            cuisines = request.form.get('cuisines', '').strip()
            description = request.form.get('description', '').strip()

            try:
                exp_years = int(years_experience) if years_experience else 0
            except ValueError:
                exp_years = 0

            maker = FoodMaker(
                user_id=user.id,
                speciality=speciality,
                years_experience=exp_years,
                cuisines=cuisines,
                description=description
            )
            maker.calculate_verification_score()
            db.session.add(maker)

        db.session.commit()

        # Log in automatically
        session.permanent = True
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name
        session['user_email'] = user.email

        flash(f'Welcome to FlavorBridge, {user.name}! Your account has been created.', 'success')

        if user.role == 'food_maker':
            return redirect(url_for('food_maker.dashboard'))
        return redirect(url_for('auth.customer_dashboard'))

    initial_role = request.args.get('role', 'customer')
    return render_template('register.html', role=initial_role)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    user_id = session.get('user_id')
    if user_id:
        existing = User.query.get(user_id)
        if not existing:
            session.clear()

    initial_role = request.args.get('role', 'customer')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        selected_role = request.form.get('role', initial_role).strip()
        next_url = request.form.get('next') or request.args.get('next')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', next=next_url, role=selected_role)

        user = User.query.filter_by(email=email).first()

        if not user or not verify_password(user.password_hash, password):
            flash('Invalid email or password. Please check your credentials.', 'danger')
            return render_template('login.html', next=next_url, role=selected_role)

        # Align role with the selected portal tab:
        if selected_role == 'food_maker':
            user.role = 'food_maker'
            maker = get_or_create_food_maker(user.id)
        elif selected_role == 'customer':
            user.role = 'customer'
        elif user.food_maker_profile or user.role == 'food_maker':
            user.role = 'food_maker'
            maker = get_or_create_food_maker(user.id)
        else:
            user.role = 'customer'
        db.session.commit()

        # Establish session
        session.permanent = True
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name
        session['user_email'] = user.email

        # Determine target redirect if next is provided
        target_redirect = None
        if next_url:
            from urllib.parse import urlparse
            parsed = urlparse(next_url)
            if parsed.path and parsed.path.startswith('/'):
                target_redirect = parsed.path
                if parsed.query:
                    target_redirect += '?' + parsed.query

        if user.role == 'food_maker':
            flash(f'Welcome to your Kitchen Dashboard, {user.name}!', 'success')
            if target_redirect:
                return redirect(target_redirect)
            return redirect(url_for('food_maker.dashboard'))
        else:
            flash(f'Welcome back, {user.name}!', 'success')
            if target_redirect:
                return redirect(target_redirect)
            return redirect(url_for('product.products_list'))

    return render_template('login.html', next=request.args.get('next'), role=initial_role)


@auth_bp.route('/maker-login')
@auth_bp.route('/login/food-maker')
def maker_login():
    """Direct portal for Food Makers."""
    if 'user_id' in session:
        if session.get('user_role') == 'food_maker':
            return redirect(url_for('food_maker.dashboard'))
        return redirect(url_for('index'))
    return redirect(url_for('auth.login', role='food_maker'))


@auth_bp.route('/login/customer')
def customer_login():
    """Direct portal for Customers."""
    if 'user_id' in session:
        return redirect(url_for('product.products_list'))
    return redirect(url_for('auth.login', role='customer'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password request page."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    initial_role = request.args.get('role', 'customer')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        selected_role = request.form.get('role', initial_role).strip()

        if not email:
            flash('Please enter your registered email address.', 'danger')
            return render_template('forgot_password.html', role=selected_role)

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with this email address. Please verify your email or create an account.', 'danger')
            return render_template('forgot_password.html', role=selected_role)

        # Store reset email in session for password update step
        session['reset_email'] = user.email
        session['reset_user_id'] = user.id
        flash(f'Account verified for {user.name}! Please enter your new password below.', 'success')
        return redirect(url_for('auth.reset_password'))

    return render_template('forgot_password.html', role=initial_role)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password page after email verification."""
    reset_email = session.get('reset_email')
    user_id = session.get('reset_user_id')

    if not reset_email or not user_id:
        flash('Session expired or invalid reset request. Please enter your email again.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(user_id)
    if not user or user.email != reset_email:
        flash('Invalid user account for reset.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            flash('Please fill in both password fields.', 'danger')
            return render_template('reset_password.html', user=user)

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('reset_password.html', user=user)

        if new_password != confirm_password:
            flash('Passwords do not match. Please ensure both passwords are identical.', 'danger')
            return render_template('reset_password.html', user=user)

        # Update password hash in database
        user.password_hash = hash_password(new_password)
        db.session.commit()

        # Clear reset session variables
        session.pop('reset_email', None)
        session.pop('reset_user_id', None)

        flash('Your password has been successfully reset! You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login', role=user.role))

    return render_template('reset_password.html', user=user)


@auth_bp.route('/logout')
def logout():
    user_name = session.get('user_name', 'there')
    session.clear()
    flash(f'Goodbye, {user_name}! You have been successfully logged out.', 'info')
    return redirect(url_for('index'))



@auth_bp.route('/customer/dashboard')
@login_required
@role_required('customer')
def customer_dashboard():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).limit(5).all()
    total_orders_count = Order.query.filter_by(customer_id=user_id).count()
    
    # Recent interactions
    recent_interactions = Interaction.query.filter_by(customer_id=user_id).order_by(Interaction.created_at.desc()).limit(6).all()
    viewed_products = [i.product for i in recent_interactions if i.product]
    
    return render_template(
        'customer_dashboard.html',
        user=user,
        recent_orders=orders,
        total_orders_count=total_orders_count,
        viewed_products=viewed_products
    )


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name', user.name).strip()
        user.phone = request.form.get('phone', user.phone).strip()
        user.city = request.form.get('city', user.city).strip()
        user.address = request.form.get('address', user.address).strip()

        new_pass = request.form.get('new_password', '').strip()
        if new_pass:
            if len(new_pass) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('profile.html', user=user)
            user.password_hash = hash_password(new_pass)

        # If food maker, update maker fields as well
        if user.role == 'food_maker' and user.food_maker_profile:
            maker = user.food_maker_profile
            maker.speciality = request.form.get('speciality', maker.speciality).strip()
            maker.cuisines = request.form.get('cuisines', maker.cuisines).strip()
            maker.description = request.form.get('description', maker.description).strip()
            try:
                maker.years_experience = int(request.form.get('years_experience', maker.years_experience))
            except ValueError:
                pass
            maker.calculate_verification_score()

        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)
